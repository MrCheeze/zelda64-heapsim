import json
import copy
import os
import queue
import threading
import multiprocessing
from . import actors, mmactors

dirname = os.path.dirname(__file__) + '/'
f=open(dirname+'/actors.json')
actorInfo = json.load(f)
f.close()

f=open(dirname+'/scenes.json')
sceneInfo = json.load(f)
f.close()

f=open(dirname+'/versions.json')
versionInfo = json.load(f)
f.close()

ACTORTYPE_ENEMY = 5

class GameState:
    def __init__(self, game, version, startFlags):
        self.game = game
        self.version = version
        self.heapStart = versionInfo[version]['heapStart']
        self.console = versionInfo[version]['console']
        self.game = versionInfo[version]['game']
        self.headerSize = 0x30 if self.console=='N64' else 0x10
        self.flags = startFlags
        self.heldActor = None

    def loadScene(self, sceneId, setupId, roomId, dayNumber=None):
        if 'ALL' in sceneInfo[self.game][sceneId]:
            self.setupData = sceneInfo[self.game][sceneId]['ALL'][setupId]
        elif self.game in sceneInfo[self.game][sceneId]:
            self.setupData = sceneInfo[self.game][sceneId][self.game][setupId]
        else:
            self.setupData = sceneInfo[self.game][sceneId][self.version][setupId]
        self.sceneId = sceneId
        self.setupId = setupId
        self.dayNumber = dayNumber
        
        self.loadedObjects = set([0x0001])
        if setupId not in [2,3]:
            self.loadedObjects.add(0x0015) # object_link_child
        if setupId not in [0,1]:
            self.loadedObjects.add(0x0014) # object_link_boy
        specialObject = self.setupData['specialObject']
        if specialObject != 0:
            self.loadedObjects.add(specialObject)

        self.actorDefs = {}
        self.actorStates = {}
        for actorId in range(len(actorInfo[self.game])):
            if 'ALL' in actorInfo[self.game][actorId]:
                actor = actorInfo[self.game][actorId]['ALL']
            elif self.console in actorInfo[self.game][actorId]:
                actor = actorInfo[self.game][actorId][self.console]
            else:
                actor = actorInfo[self.game][actorId][self.version]
            self.actorDefs[actorId] = actor

        self.ram = {}
        self.ram[self.heapStart] = HeapNode(self.heapStart, self.headerSize, 0x100000000-self.headerSize)
        
        nl = None
        if self.game == "MM":
            self.allocActor(mmactors.Player, 'ALL') # Link
            self.alloc(0x2000, 'Get Item Object')
            self.alloc(0x3800, 'Worn Mask Object')
            self.allocActor(mmactors.En_Elf, 'ALL') # Navi
        else:
            self.allocActor(actors.Player, 'ALL') # Link
            self.alloc(0x2010, 'Get Item Object')
            self.allocActor(actors.En_Elf, 'ALL') # Navi
            if self.flags['spawnFromGameOver']:
                nl = self.allocActor(actors.Magic_Dark, 'ALL') # Nayru's Love for 1 frame after game over

        self.loadedRooms = set()
        self.loadedTransitionActors = set()
        
        self.loadRoom(roomId)
        if nl is not None:
            kill = self.initFunction(nl, True)
            if kill:
                self.dealloc(nl.addr)

    def heap(self):
        nodeAddr = self.heapStart
        while nodeAddr != 0:
            yield self.ram[nodeAddr]
            nodeAddr = self.ram[nodeAddr].nextNodeAddr

    def loadRoom(self, roomId, unloadOthersImmediately=False, forceToStayLoaded=()):

        killedActors = []
        actorsToUpdate = [[],[],[],[],[],[],[],[],[],[],[],[]] # separate by actor type

        isFirstLoad = len(self.loadedRooms) == 0

        nextLoadedRooms = self.loadedRooms | {roomId}
            
        for i, transitionActor in enumerate(self.setupData['transitionActors']):
            if (transitionActor['frontRoom'] in nextLoadedRooms or transitionActor['backRoom'] in nextLoadedRooms) and i not in self.loadedTransitionActors:
                actorId = transitionActor['actorId']
                actorType = self.actorDefs[actorId]['actorType']
                loadedActor = self.allocActor(actorId, (transitionActor['frontRoom'],transitionActor['backRoom']), transitionActor['actorParams'], transitionActor['position'])
                actorsToUpdate[actorType].append(loadedActor)
                self.loadedTransitionActors.add(i)
                loadedActor.transitionActorId = i
                kill = self.initFunction(loadedActor, isFirstLoad)
                if kill:
                    killedActors.append(loadedActor)

        currentRoomClear = False
        if roomId in self.flags['clearedRooms']:
            currentRoomClear = True

        for obj in self.setupData['rooms'][roomId]['objects']:
            self.loadedObjects.add(obj)

        for actor in self.setupData['rooms'][roomId]['actors']:
            actorId = actor['actorId']
            actorType = self.actorDefs[actorId]['actorType']
            if self.game == "MM" and not actor['spawnTime'][2*self.dayNumber]:
                continue
            elif actorType == ACTORTYPE_ENEMY and currentRoomClear:
                continue
            elif self.actorDefs[actorId]['objectId'] not in self.loadedObjects:
                continue
            else:
                loadedActor = self.allocActor(actor['actorId'], (roomId,), actor['actorParams'], actor['position'])
                actorsToUpdate[actorType].append(loadedActor)
                kill = self.initFunction(loadedActor, isFirstLoad)
                if kill:
                    killedActors.append(loadedActor)
                
        for killedActor in killedActors:
            self.dealloc(killedActor.addr)

        self.loadedRooms = nextLoadedRooms

        if unloadOthersImmediately:
            self.unloadRoomsExcept(roomId, forceToStayLoaded=forceToStayLoaded)

        killedActors = []
        for actorType in range(12):
            for loadedActor in actorsToUpdate[actorType]:
                if not loadedActor.free:
                    kill = self.updateFunction(loadedActor, isFirstLoad)
                    if kill:
                        killedActors.append(loadedActor)
        for killedActor in killedActors:
            self.dealloc(killedActor.addr)

    def unloadRoomsExcept(self, roomId, forceToStayLoaded=()):

        assert roomId in self.loadedRooms
        self.loadedRooms = set([roomId])
            
        for node in self.heap():
            if not node.free and node.rooms != 'ALL':
                if node.addr in forceToStayLoaded:
                    node.rooms = 'FORCE_STAY_LOADED'
                    continue
                for actorRoomId in node.rooms:
                    if actorRoomId in self.loadedRooms:
                        break
                else:
                    self.dealloc(node.addr)

    def changeRoom(self, roomId, forceToStayLoaded=()):
        self.loadRoom(roomId, unloadOthersImmediately=True, forceToStayLoaded=forceToStayLoaded)

    def allocActor(self, actorId, rooms='ALL', actorParams=0x0000, position=(0,0,0), held=False):

        if actorId not in self.actorStates:
            self.actorStates[actorId] = {'numLoaded':0}
        actorState = self.actorStates[actorId]
        actorDef = self.actorDefs[actorId]

        if actorState['numLoaded'] == 0 and actorDef['overlaySize'] and actorDef['allocType']==0:
            overlayNode = self.alloc(actorDef['overlaySize'], 'Overlay %04X %s'%(actorId,actorDef['name']))
            actorState['loadedOverlay'] = overlayNode.addr

        instanceNode = self.alloc(actorDef['instanceSize'], 'Actor %04X %s (%04X)'%(actorId,actorDef['name'],actorParams))
        instanceNode.rooms = rooms
        instanceNode.nodeType = 'INSTANCE'
        instanceNode.actorId = actorId
        instanceNode.actorParams = actorParams
        instanceNode.position = position
        instanceNode.parent = None

        if held:
            assert self.heldActor is None
            self.heldActor = instanceNode.addr

        actorState['numLoaded'] += 1

        return instanceNode

    def allocMultipleActors(self, actorId, count, rooms='ALL', actorParams=0x0000, position=(0,0,0), parentAddr=None):
        children = []
        for i in range(count):
            child = self.allocActor(actorId, rooms, actorParams, position)
            child.parent = parentAddr
            children.append(child.addr)

        if parentAddr is not None:
            parent = self.ram[parentAddr]
            assert not parent.spawnedChildren
            parent.spawnedChildren = tuple(children)

    def allocAndInitActor(self, actorId, rooms='ALL', actorParams=0x0000, position=(0,0,0), held=False):
        instanceNode = self.allocActor(actorId, rooms, actorParams, position, held)
        assert not self.initFunction(instanceNode, False)
        assert not self.updateFunction(instanceNode, False)
        return instanceNode

    def alloc(self, allocSize, description):
        allocSize = allocSize + ((-allocSize)%0x10)
        for node in self.heap():
            if node.free and node.blockSize >= allocSize:
                if node.blockSize > allocSize + self.headerSize:
                    newNode = HeapNode(node.addr+self.headerSize+allocSize, self.headerSize, node.blockSize-allocSize-self.headerSize)
                    self.ram[newNode.addr] = newNode
                    node.blockSize = allocSize
                    newNode.prevNodeAddr = node.addr
                    newNode.nextNodeAddr = node.nextNodeAddr
                    if node.nextNodeAddr:
                        self.ram[node.nextNodeAddr].prevNodeAddr = newNode.addr
                    node.nextNodeAddr = newNode.addr
                node.free = False
                node.description = description
                return node
        raise Exception('alloc should always succeed')

    def dealloc(self, nodeAddr, nodeDesc=None):
        node = self.ram[nodeAddr]
        assert not node.free
        if nodeDesc is not None:
            assert node.description == nodeDesc

        if node.nodeType == 'INSTANCE':

            self.destroyFunction(node)
            
            actorDef = self.actorDefs[node.actorId]
            actorState = self.actorStates[node.actorId]
            actorState['numLoaded'] -= 1
            if actorState['numLoaded'] == 0 and actorDef['overlaySize'] and actorDef['allocType']==0:
                self.dealloc(actorState['loadedOverlay'])

            if node.parent:
                parent = self.ram[node.parent]
                parent.spawnedChildren = tuple([addr for addr in parent.spawnedChildren if addr != nodeAddr])

            if self.heldActor == nodeAddr:
                self.heldActor = None

        if node.transitionActorId is not None:
            self.loadedTransitionActors.remove(node.transitionActorId)
        
        if self.ram[node.nextNodeAddr].free:
            node.blockSize += self.headerSize + self.ram[node.nextNodeAddr].blockSize
            node.nextNodeAddr = self.ram[node.nextNodeAddr].nextNodeAddr
            if node.nextNodeAddr > 0:
                self.ram[node.nextNodeAddr].prevNodeAddr = node.addr
        if self.ram[node.prevNodeAddr].free:
            self.ram[node.prevNodeAddr].blockSize += self.headerSize + node.blockSize
            self.ram[node.prevNodeAddr].nextNodeAddr = node.nextNodeAddr
            if node.nextNodeAddr > 0:
                self.ram[node.nextNodeAddr].prevNodeAddr = node.prevNodeAddr
                
        node.reset()

    def explode(self, nodeAddr, room, nodeDesc=None):
        node = self.ram[nodeAddr]
        if node.actorId == mmactors.En_Bom:
            self.allocActor(mmactors.En_Clear_Tag, (room,), 0x0000, (0,0,0))
        elif node.actorId == mmactors.Obj_Tsubo:
            self.allocActor(mmactors.En_Item00, 'ALL', 0x0000, (0,0,0))
        else:
            assert False
        self.dealloc(nodeAddr, nodeDesc)

    def pickup(self, nodeAddr, nodeDesc=None):
        node = self.ram[nodeAddr]
        node.rooms = 'ALL'
        self.heldActor = nodeAddr

    def drop(self, nodeAddr, room, nodeDesc=None):
        node = self.ram[nodeAddr]
        node.rooms = (room,)
        self.heldActor = None

    def unloadChildren(self, nodeAddr):
        node = self.ram[nodeAddr]
        for childAddr in node.spawnedChildren:
            self.dealloc(childAddr)
        node.spawnedChildren = ()

    def initFunction(self, node, isFirstLoad): ### Incomplete -- need to add all behaviour here that matters for heap manip.

        kill = False

        if self.game == "OoT":
            if node.actorId == actors.En_River_Sound and node.actorParams==0x000C and (not self.flags['lullaby'] or self.flags['saria']): # Proximity Saria's Song
                kill = True

            elif node.actorId == actors.Object_Kankyo:
                node.rooms = 'ALL'
                if self.actorStates[node.actorId]['numLoaded'] > 1 and node.actorParams != 0x0004:
                    kill = True

            elif node.actorId == actors.Door_Warp1 and node.actorParams == 0x0006:
                kill = True

            elif node.actorId == actors.Obj_Bean and self.setupId in [2,3] and not self.flags['beanPlanted']:
                kill = True

            elif node.actorId == actors.Bg_Spot02_Objects and self.setupId in [2,3] and node.actorParams == 0x0001:
                kill = True

            elif node.actorId == actors.En_Weather_Tag and node.actorParams == 0x1405:
                kill = True

            elif node.actorId == actors.En_Wonder_Item:
                wonderItemType = node.actorParams >> 0xB
                switchFlag = node.actorParams & 0x003F
                if wonderItemType == 1 or wonderItemType == 6 or wonderItemType > 9:
                    kill = True
                elif switchFlag in self.flags['switchFlags']:
                    kill = True

            elif node.actorId == actors.En_Owl and self.sceneId == 0x5B and (not self.flags['lullaby']):
                kill = True

            elif node.actorId in [actors.Obj_Bombiwa, actors.En_Wonder_Talk2]:
                switchFlag = node.actorParams & 0x003F
                if switchFlag in self.flags['switchFlags']:
                    kill = True

            elif node.actorId == actors.En_Item00:
                collectibleFlag = (node.actorParams & 0x3F00) // 0x100
                if collectibleFlag in self.flags['collectibleFlags']:
                    kill = True

            elif node.actorId == actors.Obj_Oshihiki and node.actorParams == 0x2044:
                kill = True

            elif node.actorId == actors.Bg_Breakwall and node.actorParams in [0x0007, 0xA01F]:
                kill = True

            elif node.actorId == actors.Magic_Dark:
                kill = True

            elif node.actorId == actors.En_Ru1 and 2 in node.rooms and self.flags['rutoFellInHole']:
                kill = True
                
            elif node.actorId in [actors.En_Ko, actors.En_Md, actors.En_Sa] and isFirstLoad:
                self.allocActor(actors.En_Elf, rooms=node.rooms)

            elif node.actorId in [actors.Obj_Makeoshihiki]:
                self.allocActor(actors.Obj_Oshihiki, rooms=node.rooms)
                node.spawnedChildren = ()

            elif node.actorId in [actors.Obj_Mure, actors.Obj_Mure2, actors.Obj_Mure3]:
                node.spawnedChildren = ()
                if node.actorId == actors.Obj_Mure2:
                    if node.actorParams & 3 == 1: # bushes
                        node.childCount = 12
                    if node.actorParams & 3 == 2: # rocks
                        node.childCount = 8
                if node.actorId == actors.Obj_Mure3:
                    if node.actorParams & 0xE000 == 0x4000:
                        node.childCount = 7
        else: # MM

            if node.actorId == mmactors.En_Test4:
                node.rooms = 'ALL'
                if self.actorStates[mmactors.En_Test4]['numLoaded'] > 1:
                    kill = True
            elif node.actorId == mmactors.En_Mnk:
                if node.actorParams == 0x6B83:
                    if self.version == 'MM-J-1.0':
                        if self.actorStates[mmactors.En_Mnk]['numLoaded'] > 1:
                            kill = True
                        else:
                            node.rooms = 'ALL'
                    else:
                        if not isFirstLoad:
                            kill = True
                        else:
                            node.rooms = 'ALL'
            elif node.actorId == mmactors.En_M_Thunder:
                if self.flags['magic']:
                    node.dust = self.allocActor(mmactors.Eff_Dust, 'ALL', 0x0000, (0,0,0)).addr
                else:
                    node.dust = None
            elif node.actorId == mmactors.En_Kakasi and not isFirstLoad:
                self.alloc(0xB0, 'SkelAnime')
                self.alloc(0xB0, 'SkelAnime')

        return kill
            

    def updateFunction(self, node, isFirstLoad): ### Also incomplete -- This sim runs update on all actors just once after loading.

        kill = False

        if self.game == "OoT":
            if node.actorId in [actors.En_Ko, actors.En_Md, actors.En_Sa] and not isFirstLoad:
                self.allocActor(actors.En_Elf, rooms=node.rooms)

        else: # MM
            if node.actorId == mmactors.En_Holl:
                if 1 <= int(self.dayNumber) <= 3 and (node.actorParams & 0x0380) == 0:
                    dayFlags = node.actorParams & 7
                    if not dayFlags & (1 << (int(self.dayNumber)-1)):
                        kill = True
            elif node.actorId == mmactors.En_Trt2:
                node.skelAnime1 = self.alloc(0xB0, 'SkelAnime').addr
                node.skelAnime2 = self.alloc(0xB0, 'SkelAnime').addr
            elif node.actorId == mmactors.En_Kakasi and isFirstLoad:
                self.alloc(0xB0, 'SkelAnime')
                self.alloc(0xB0, 'SkelAnime')

        return kill

    def destroyFunction(self, node):
        if self.game == "MM":
            if node.actorId == mmactors.En_Trt2:
                self.dealloc(node.skelAnime1)
                self.dealloc(node.skelAnime2)
            elif node.actorId == mmactors.En_M_Thunder:
                if node.dust is not None:
                    self.dealloc(node.dust)

    def getAvailableActions(self, carryingActor, disableInteractionWith=[], ignoreRooms={}, disableInteractionWithAddrs=[]): ### Also incomplete.

        if self.game == "MM":
            return self.getAvailableActionsMM(carryingActor, disableInteractionWith, ignoreRooms)

        availableActions = set()

        if len(self.loadedRooms) > 1:
            for room in self.loadedRooms:
                availableActions.add(('unloadRoomsExcept', room))

        for actorId in (actors.En_M_Thunder,actors.En_Bom,actors.En_Bom_Chu,actors.En_Insect,actors.En_Fish,actors.En_Boom,actors.En_Item00,actors.En_Ishi,actors.En_Kusa,actors.Arms_Hook,actors.En_Arrow):
            if actorId not in self.actorStates:
                self.actorStates[actorId] = {'numLoaded':0}

        if not carryingActor and self.actorStates[actors.En_M_Thunder]['numLoaded'] < 1 and self.actorStates[actors.Arms_Hook]['numLoaded'] < 1:
        
            if self.flags['bombchu'] and self.actorStates[actors.En_Bom]['numLoaded'] + self.actorStates[actors.En_Bom_Chu]['numLoaded'] < 3:
                if len(self.loadedRooms) == 1:
                    availableActions.add(('allocActor', actors.En_Bom_Chu, tuple(self.loadedRooms)))
                else:
                    availableActions.add(('allocActor', actors.En_Bom_Chu))
            
            if self.flags['bomb'] and self.actorStates[actors.En_Bom]['numLoaded'] + self.actorStates[actors.En_Bom_Chu]['numLoaded'] < 3:
                if len(self.loadedRooms) == 1:
                    availableActions.add(('allocActor', actors.En_Bom, tuple(self.loadedRooms)))
                else:
                    availableActions.add(('allocActor', actors.En_Bom))

            if self.flags['bottle'] and self.actorStates[actors.En_Insect]['numLoaded'] < 1: # dropping more than 1 bugs is a mess
                if len(self.loadedRooms) == 1:
                    availableActions.add(('allocMultipleActors', actors.En_Insect, 3, tuple(self.loadedRooms)))
                else:
                    availableActions.add(('allocMultipleActors', actors.En_Insect, 3))

            if self.flags['bottle'] and self.actorStates[actors.En_Fish]['numLoaded'] < 1: # to a lesser extent, true for fish also
                if len(self.loadedRooms) == 1:
                    availableActions.add(('allocActor', actors.En_Fish, tuple(self.loadedRooms)))
                else:
                    availableActions.add(('allocActor', actors.En_Fish))

            if self.flags['sword']:
                if len(self.loadedRooms) == 1:
                    availableActions.add(('allocActor', actors.En_M_Thunder, tuple(self.loadedRooms)))
                else:
                    availableActions.add(('allocActor', actors.En_M_Thunder))

            if self.flags['hookshot']:
                if len(self.loadedRooms) == 1:
                    availableActions.add(('allocActor', actors.Arms_Hook, tuple(self.loadedRooms)))
                else:
                    availableActions.add(('allocActor', actors.Arms_Hook))

            if self.flags['boomerang'] and self.actorStates[actors.En_Boom]['numLoaded'] < 1:
                if len(self.loadedRooms) == 1:
                    availableActions.add(('allocActor', actors.En_Boom, tuple(self.loadedRooms)))
                else:
                    availableActions.add(('allocActor', actors.En_Boom))

            if self.flags['slingshot'] and self.actorStates[actors.En_Arrow]['numLoaded'] < 3:
                if len(self.loadedRooms) == 1:
                    availableActions.add(('allocActor', actors.En_Arrow, tuple(self.loadedRooms)))
                else:
                    availableActions.add(('allocActor', actors.En_Arrow))

        if len(self.loadedRooms) == 1: # assume without loss of generality that we only despawn actors when not in loading transitions
              
            for node in self.heap():
                if not node.free and node.nodeType=='INSTANCE' and node.actorId not in disableInteractionWith and node.addr not in disableInteractionWithAddrs:
                    
                    if node.rooms != 'ALL' and len(node.rooms) > 1 and len(self.loadedRooms) == 1: # This is a transition actor
                        for room in node.rooms:
                            if room not in self.loadedRooms and room not in ignoreRooms:
                                if node.actorId == actors.En_Holl and node.actorParams & 0x01C0 == 0x0000:
                                    availableActions.add(('loadRoom', room))
                                else:
                                    availableActions.add(('changeRoom', room))

                    if node.actorId in [actors.En_Bom, actors.En_Bom_Chu, actors.En_Insect, actors.En_Fish, actors.En_M_Thunder, actors.En_Boom, actors.Arms_Hook, actors.En_Item00, actors.En_Arrow]:
                        availableActions.add(('dealloc', node.addr, node.description))

                    if not carryingActor and self.actorStates[actors.En_M_Thunder]['numLoaded'] < 1 and self.actorStates[actors.Arms_Hook]['numLoaded'] < 1: # less safe assumption, but go with it for now...
              
                        if node.actorId in [actors.En_Wonder_Item, actors.En_Kusa, actors.En_Ishi, actors.Obj_Bombiwa, actors.En_Firefly, actors.Obj_Tsubo, actors.En_Okuta, actors.En_Bubble, actors.En_Bili, actors.Obj_Kibako]:
                            availableActions.add(('dealloc', node.addr, node.description))
                            
                        if node.actorId == actors.En_Kanban:
                            availableActions.add(('allocActor', actors.En_Kanban, tuple(node.rooms)))

                    if node.actorId == actors.Obj_Mure2:
                        if node.spawnedChildren:
                          if self.actorStates[actors.En_Boom]['numLoaded'] < 1: # hmm
                            availableActions.add(('unloadChildren', node.addr))
                        else:
                            if node.actorParams & 3 == 1: # bushes
                                availableActions.add(('allocMultipleActors', actors.En_Kusa, node.childCount, tuple(node.rooms), 0x0000, (0,0,0), node.addr))
                            if node.actorParams & 3 == 2: # rocks
                                availableActions.add(('allocMultipleActors', actors.En_Ishi, node.childCount, tuple(node.rooms), 0x0000, (0,0,0), node.addr))
                    if node.actorId == actors.Obj_Mure3:
                        if node.spawnedChildren:
                          if self.actorStates[actors.En_Boom]['numLoaded'] < 1: # hmm
                            availableActions.add(('unloadChildren', node.addr))
                        else:
                            if node.actorParams & 0xE000 == 0x4000:
                                availableActions.add(('allocMultipleActors', actors.En_Item00, node.childCount, tuple(node.rooms), 0x4000, (0,0,0), node.addr))
            

        return availableActions

    def getAvailableActionsMM(self, carryingActor, disableInteractionWith=[], ignoreRooms={}): ### Also incomplete.
        availableActions = set()

        if len(self.loadedRooms) > 1:
            for room in self.loadedRooms:
                availableActions.add(('unloadRoomsExcept', room))

        for actorId in (mmactors.En_M_Thunder,mmactors.Arms_Hook,mmactors.En_Bom,mmactors.En_Bom_Chu):
            if actorId not in self.actorStates:
                self.actorStates[actorId] = {'numLoaded':0}

        if not carryingActor and self.heldActor is None:

            if self.flags['sword']:
                availableActions.add(('allocAndInitActor', mmactors.En_M_Thunder, 'ALL', 0x0000, (0,0,0), True))
            
            if self.flags['bomb'] and self.actorStates[mmactors.En_Bom]['numLoaded'] + self.actorStates[mmactors.En_Bom_Chu]['numLoaded'] < 3:
                availableActions.add(('allocActor', mmactors.En_Bom, 'ALL', 0x0000, (0,0,0), True))
              
        for node in self.heap():
            if not node.free and node.nodeType=='INSTANCE' and node.actorId not in disableInteractionWith:
                
                if node.rooms != 'ALL' and len(node.rooms) > 1 and len(self.loadedRooms) == 1: # This is a transition actor
                    for room in node.rooms:
                        if room not in self.loadedRooms and room not in ignoreRooms:
                            if node.actorId == mmactors.En_Holl:
                                #availableActions.add(('loadRoom', room))
                                availableActions.add(('changeRoom', room))
                    
                if node.actorId == mmactors.En_Bom:
                    for room in self.loadedRooms:
                        availableActions.add(('explode', node.addr, room, node.description))
                        if self.heldActor == node.addr:
                            availableActions.add(('drop', node.addr, room, node.description))
                        else:
                            pass#availableActions.add(('pickup', node.addr, node.description))
        
                if len(self.loadedRooms) == 1:

                    if node.actorId in [mmactors.En_M_Thunder, mmactors.En_Mnk, mmactors.En_Clear_Tag, mmactors.En_Item00]:
                        availableActions.add(('dealloc', node.addr, node.description))
                                    
                    if not carryingActor and (self.heldActor is None or self.heldActor == node.addr):
              
                        if node.actorId in [mmactors.En_Kusa, mmactors.Obj_Tsubo]:
                            if not (self.sceneId == 0x29 and len(node.rooms) == 1 and 0 in node.rooms):
                                availableActions.add(('dealloc', node.addr, node.description))
                                if self.heldActor != node.addr:
                                    pass#availableActions.add(('pickup', node.addr, node.description))
                                if node.actorId == mmactors.Obj_Tsubo and not (self.sceneId == 0x29 and 0 in self.loadedRooms):
                                    pass#availableActions.add(('explode', node.addr, 'ALL', node.description))

        return availableActions

    def search(self, successFunction, carryingActor=False, disableInteractionWith=[], actionLimit=None, printProgress=True, num_worker_threads=None,ignoreRooms={},disableInteractionWithAddrs=[]):

        if num_worker_threads is None:
            num_worker_threads = multiprocessing.cpu_count()
            num_worker_threads = 12

        seenStates = set()
        maxActionCount = -1
        ret = None

        def worker():
            nonlocal ret
            while ret is None:
                try:
                    actionList = actionsQueue.get(timeout=1)
                except queue.Empty:
                    return

                nonlocal maxActionCount
                if len(actionList) > maxActionCount:
                    maxActionCount = len(actionList)
                    if printProgress:
                        print('--- %d ---\n'%maxActionCount,end='')
                    
                stateCopy = copy.deepcopy(self)
                for action in actionList:
                    func = getattr(stateCopy, action[0])
                    func(*action[1:])

                stateHash = hash(stateCopy)
                if stateHash not in seenStates:
                    seenStates.add(stateHash)

                    if successFunction(stateCopy, tuple(actionList)):
                        if printProgress:
                            print('Solved!!!\nSolved!!!\nSolved!!!\n',end='')
                            print('Solved!!!\nSolved!!!\nSolved!!!\n',end='')
                            print('Solved!!!\nSolved!!!\nSolved!!!\n',end='')
                        ret = (stateCopy, actionList)
                    elif actionLimit is None or len(actionList) < actionLimit:
                        for action in stateCopy.getAvailableActions(carryingActor, disableInteractionWith, ignoreRooms, disableInteractionWithAddrs):
                            newActionList = actionList + (action,)
                            actionsQueue.put(TupleWrapper(newActionList))

                actionsQueue.task_done()

        actionsQueue = queue.PriorityQueue()
        
        threads = []
        for i in range(num_worker_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
            
        actionsQueue.put(TupleWrapper(()))

        for t in threads:
            t.join()

        return ret

    def __str__(self):
        return "\n".join((str(node) for node in self.heap()))

    def __hash__(self):
        return hash(tuple(self.heap()))

    def __deepcopy__(self, memo):
        selfCopy = copy.copy(self)
        selfCopy.loadedObjects = copy.copy(self.loadedObjects)
        selfCopy.loadedRooms = copy.copy(self.loadedRooms)
        selfCopy.loadedTransitionActors = copy.copy(self.loadedTransitionActors)
        selfCopy.actorStates = copy.deepcopy(self.actorStates) # why is this necessary?
        selfCopy.ram = {}
        for node in self.heap():
            selfCopy.ram[node.addr] = copy.copy(node)
        return selfCopy

class HeapNode:
    def __init__(self, addr, headerSize, blockSize):
        self.addr = addr
        self.headerSize = headerSize
        self.blockSize = blockSize
        self.prevNodeAddr = 0
        self.nextNodeAddr = 0
        self.reset()

    def reset(self):
        self.free = True
        self.description = 'Empty'
        self.rooms = 'ALL'
        self.nodeType = 'OTHER'
        self.actorId = None
        self.actorParams = None
        self.transitionActorId = None

    def __str__(self):
        return "header:%08X data:%08X free:%d blocksize:%X next_addr:%X prev_addr:%X - %s"%(self.addr,self.addr+self.headerSize,self.free,self.blockSize, self.nextNodeAddr, self.prevNodeAddr, self.description)

    def __hash__(self):
        return hash((self.addr, self.headerSize, self.blockSize, self.prevNodeAddr, self.nextNodeAddr, self.free, self.description, self.rooms, self.nodeType, self.actorId, self.actorParams, self.transitionActorId))


class TupleWrapper(tuple):
    def __lt__(self, other):
        return len(self) < len(other)
    def __le__(self, other):
        return len(self) <= len(other)
    def __eq__(self, other):
        return len(self) == len(other)
    def __ne__(self, other):
        return len(self) != len(other)
    def __gt__(self, other):
        return len(self) > len(other)
    def __ge__(self, other):
        return len(self) >= len(other)


