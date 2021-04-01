import json
import copy
import os
import queue
import threading
import multiprocessing
import random
from . import actors

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

    def loadScene(self, sceneId, roomId):
        if 'ALL' in sceneInfo[self.game][sceneId]:
            sceneData = sceneInfo[self.game][sceneId]['ALL']
        elif self.game in sceneInfo[self.game][sceneId]:
            sceneData = sceneInfo[self.game][sceneId][self.game]
        else:
            sceneData = sceneInfo[self.game][sceneId][self.version]
        setupId = self.flags['adult']*2 + self.flags['night']*1
        while sceneData[setupId] is None:
            setupId -= 1
        self.setupData = sceneData[setupId]
        self.sceneId = sceneId
        
        self.loadedObjects = set([0x0001, 0x0014, 0x0015])
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
        
        self.allocActor(actors.Player, 'ALL') # Link
        self.alloc(0x2010, 'Get Item Object')
        self.allocActor(actors.En_Elf, 'ALL') # Navi

        self.loadedRooms = set()
        
        self.loadRoom(roomId)

    def heap(self):
        nodeAddr = self.heapStart
        while nodeAddr != 0:
            yield self.ram[nodeAddr]
            nodeAddr = self.ram[nodeAddr].nextNodeAddr

    def loadRoom(self, roomId, unloadOthersImmediately=False, forceToStayLoaded=()):
        for transitionActor in self.setupData['transitionActors']:
            if (transitionActor['frontRoom'] == roomId or transitionActor['backRoom'] == roomId) and transitionActor['frontRoom'] not in self.loadedRooms and transitionActor['backRoom'] not in self.loadedRooms:
                self.allocActor(transitionActor['actorId'], [transitionActor['frontRoom'],transitionActor['backRoom']])

        currentRoomClear = False
        if roomId in self.flags['clearedRooms']:
            currentRoomClear = True

        for obj in self.setupData['rooms'][roomId]['objects']:
            self.loadedObjects.add(obj)

        actorsToInit = []
        actorsToUpdate = [[],[],[],[],[],[],[],[],[],[],[],[]] # separate by actor type
            
        for actor in self.setupData['rooms'][roomId]['actors']:
            actorId = actor['actorId']
            actorType = self.actorDefs[actorId]['actorType']
            if actorType == ACTORTYPE_ENEMY and currentRoomClear:
                continue
            elif self.actorDefs[actorId]['objectId'] not in self.loadedObjects:
                continue
            else:
                loadedActor = self.allocActor(actor['actorId'], [roomId], actor['actorParams'], actor['position'])
                actorsToInit.append(loadedActor)
                if loadedActor.actorId == actors.En_Md and len(self.loadedRooms) > 0: # hack hack hack
                    self.updateFunction(loadedActor)
                else:
                    actorsToUpdate[actorType].append(loadedActor)

        for actorType in range(12):
            for loadedActor in actorsToInit:
                self.initFunction(loadedActor)

        self.loadedRooms.add(roomId)

        if unloadOthersImmediately:
            self.unloadRoomsExcept(roomId, forceToStayLoaded=forceToStayLoaded)

        for actorType in range(12):
            for loadedActor in actorsToUpdate[actorType]:
                if not loadedActor.free:
                    self.updateFunction(loadedActor)

    def unloadRoomsExcept(self, roomId, forceToStayLoaded=()):

        assert roomId in self.loadedRooms
        self.loadedRooms = set([roomId])
            
        for node in self.heap():
            if node.actorId == actors.En_Skj:
                node.active = True
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

    def allocActor(self, actorId, rooms='ALL', actorParams=0x0000, position=(0,0,0)):

        if actorId not in self.actorStates:
            self.actorStates[actorId] = {'numLoaded':0}
        actorState = self.actorStates[actorId]
        actorDef = self.actorDefs[actorId]

        if actorState['numLoaded'] == 0 and actorDef['overlaySize'] and actorDef['allocType']==0:
            overlayNode = self.alloc(actorDef['overlaySize'], 'Overlay %04X %s'%(actorId,actorDef['name']))
            actorState['loadedOverlay'] = overlayNode.addr

        instanceNode = self.alloc(actorDef['instanceSize'], 'Actor %04X %s (%04X)'%(actorId,actorDef['name'],actorParams))
        instanceNode.rooms = tuple(rooms) if type(rooms) is list else rooms
        instanceNode.nodeType = 'INSTANCE'
        instanceNode.actorId = actorId
        instanceNode.actorParams = actorParams
        instanceNode.position = tuple(position)

        actorState['numLoaded'] += 1

        return instanceNode

    def allocMultipleActors(self, actorId, count, rooms='ALL', actorParams=0x0000, position=(0,0,0)):
        for i in range(count):
            self.allocActor(actorId, rooms, actorParams, position)

    def songOfStorms(self, roomId):
        oca = self.allocActor(actors.Oceff_Storm)
        rain = self.allocActor(actors.En_Okarina_Effect, rooms=[roomId])
        self.dealloc(oca.addr)
        return rain

    def loadAllNeedles(self, rooms):
        for node in self.heap():
            if node.actorId == actors.En_Skj and node.active:
                self.allocMultipleActors(actors.En_Skjneedle, node.numNeedlesRemaining, rooms)
                node.numNeedlesRemaining = 0
        for node in self.heap():
            if node.actorId == actors.En_Skj and node.active:
                self.dealloc(node.addr)

    def loadNeedles(self, skullKidAddr, rooms):
        node = self.ram[skullKidAddr]
        self.allocMultipleActors(actors.En_Skjneedle, 3, rooms)
        node.numNeedlesRemaining -= 3
        if node.numNeedlesRemaining == 0:
            self.dealloc(skullKidAddr)

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

    def dealloc(self, nodeAddr):
        node = self.ram[nodeAddr]
        assert not node.free

        if node.nodeType == 'INSTANCE':
            actorDef = self.actorDefs[node.actorId]
            actorState = self.actorStates[node.actorId]
            actorState['numLoaded'] -= 1
            if actorState['numLoaded'] == 0 and actorDef['overlaySize'] and actorDef['allocType']==0:
                self.dealloc(actorState['loadedOverlay'])
        
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

    def initFunction(self, node): ### Incomplete -- need to add all behaviour here that matters for heap manip.

        if node.actorId == actors.En_River_Sound and node.actorParams==0x000C and (not self.flags['lullaby'] or self.flags['saria']): # Proximity Saria's Song
            self.dealloc(node.addr)

        elif node.actorId == actors.Object_Kankyo:
            node.rooms = 'ALL'
            if self.actorStates[node.actorId]['numLoaded'] > 1 and node.actorParams != 0x0004:
                self.dealloc(node.addr)

        elif node.actorId == actors.Door_Warp1 and node.actorParams == 0x0006:
            self.dealloc(node.addr)

        elif node.actorId == actors.Obj_Bean and self.flags['adult'] and not self.flags['beanPlanted']:
            self.dealloc(node.addr)

        elif node.actorId == actors.Bg_Spot02_Objects and self.flags['adult'] and node.actorParams == 0x0001:
            self.dealloc(node.addr)

        elif node.actorId == actors.En_Weather_Tag and node.actorParams == 0x1405:
            self.dealloc(node.addr)

        elif node.actorId == actors.En_Wonder_Item:
            wonderItemType = node.actorParams >> 0xB
            switchFlag = node.actorParams & 0x003F
            if wonderItemType == 1 or wonderItemType == 6 or wonderItemType > 9:
                self.dealloc(node.addr)
            elif switchFlag in self.flags['switchFlags']:
                self.dealloc(node.addr)

        elif node.actorId == actors.En_Owl and self.sceneId == 0x5B and (not self.flags['lullaby']):
            self.dealloc(node.addr)

        elif node.actorId in [actors.Obj_Bombiwa, actors.En_Wonder_Talk2]:
            switchFlag = node.actorParams & 0x003F
            if switchFlag in self.flags['switchFlags']:
                self.dealloc(node.addr)

        elif node.actorId == actors.En_Item00:
            collectibleFlag = (node.actorParams & 0x3F00) // 0x100
            if collectibleFlag in self.flags['collectibleFlags']:
                self.dealloc(node.addr)

        elif node.actorId == actors.En_Skj:
            node.numNeedlesRemaining = 21
            if tuple(node.position) == (1265, -94, 420) or tuple(node.position) == (-1132, 80, -128):
                node.active = False
            else:
                node.active = True

        elif node.actorId == actors.En_Ko: # temp for lost woods
            self.dealloc(node.addr)

    def updateFunction(self, node): ### Also incomplete -- This sim runs update on all actors just once after loading.

        if node.actorId in [actors.En_Ko, actors.En_Md, actors.En_Sa]:
            self.allocActor(actors.En_Elf, rooms=node.rooms)

    def getAvailableActions(self, carryingActor): ### Also incomplete.

        availableActions = []

        for actorId in (actors.En_M_Thunder,actors.En_Bom,actors.En_Bom_Chu,actors.En_Insect,actors.En_Fish,actors.Arms_Hook,actors.En_Okarina_Effect,actors.En_Skjneedle):
            if actorId not in self.actorStates:
                self.actorStates[actorId] = {'numLoaded':0}

        if len(self.loadedRooms) > 1:
            for room in self.loadedRooms:
                availableActions.append(['unloadRoomsExcept', room])

        if not carryingActor and self.actorStates[actors.En_M_Thunder]['numLoaded'] < 1:
        
            if self.flags['bombchu'] and self.actorStates[actors.En_Bom]['numLoaded'] + self.actorStates[actors.En_Bom_Chu]['numLoaded'] < 3:
                availableActions.append(['allocActor', actors.En_Bom_Chu])
            
            if self.flags['bomb'] and self.actorStates[actors.En_Bom]['numLoaded'] + self.actorStates[actors.En_Bom_Chu]['numLoaded'] < 3:
                availableActions.append(['allocActor', actors.En_Bom])

            if self.flags['bottle'] and self.actorStates[actors.En_Insect]['numLoaded'] < 3: # dropping more than 1 bugs is a mess
                availableActions.append(['allocMultipleActors', actors.En_Insect, 3])

            #if self.flags['bottle'] and self.actorStates[actors.En_Fish]['numLoaded'] < 1: # to a lesser extent, true for fish also
            #    availableActions.append(['allocActor', actors.En_Fish])

            if self.flags['hookshot'] and self.actorStates[actors.Arms_Hook]['numLoaded'] < 1:
                availableActions.append(['allocActor', actors.Arms_Hook])

            if self.flags['storms'] and self.actorStates[actors.En_Okarina_Effect]['numLoaded'] < 1:
                for room in self.loadedRooms:
                    availableActions.append(['songOfStorms', room])

            #availableActions.append(['allocActor', actors.En_M_Thunder])
              
        for node in self.heap():
            if not node.free and node.nodeType=='INSTANCE':

                if len(self.loadedRooms) == 1: # assume without loss of generality that we only despawn actors when not in loading transitions
                
                    if node.rooms != 'ALL' and len(node.rooms) > 1 and len(self.loadedRooms) == 1: # This is a transition actor
                        for room in node.rooms:
                            if room not in self.loadedRooms and room not in [2,4]: # hack
                                availableActions.append(['loadRoom', room])

                    #if node.actorId in [actors.En_Bom, actors.En_Bom_Chu, actors.En_Insect, actors.En_Fish, actors.En_M_Thunder, actors.En_Okarina_Effect]:
                    #    availableActions.append(['dealloc', node.addr])

                    if not carryingActor and self.actorStates[actors.En_M_Thunder]['numLoaded'] < 1: # less safe assumption, but go with it for now...
              
                        if node.actorId in [actors.En_Wonder_Item, actors.En_Kusa, actors.Obj_Bombiwa]:
                            if node.actorId != actors.Obj_Bombiwa: #hack hack
                                availableActions.append(['dealloc', node.addr])

                if node.actorId == actors.En_Skj:
                    for room in self.loadedRooms: #(1265, -94, 420)
                        if self.actorStates[actors.En_Insect]['numLoaded'] < 3:
                            if node.numNeedlesRemaining >= 21 and node.active:
                                availableActions.append(['loadAllNeedles', (room,)])
                            if node.numNeedlesRemaining >= 3 and node.active:
                                availableActions.append(['loadNeedles', node.addr, (room,)])
            

        return availableActions

    def search(self, successFunction, carryingActor=False, maxDepth=float('inf')):

        num_worker_threads = multiprocessing.cpu_count()

        seenStates = set()
        maxActionCount = -1
        ret = None

        def worker():
            nonlocal ret
            while ret is None:
                try:
                    actionList_ = actionsQueue.get(timeout=5)
                except queue.Empty:
                    return
                if actionList_ == 'DONE':
                    return

                #print(actionList_)
                actionList, bushrots, drawptrs = actionList_

                nonlocal maxActionCount
                if len(actionList) > maxActionCount:
                    maxActionCount = len(actionList)
                    print('--- %d ---\n'%maxActionCount,end='')
                if len(actionList) > maxDepth:
                    for i in range(num_worker_threads):
                        actionsQueue.put('DONE')
                    #print('giving up, too long.\n',end='')
                    return

                #print('%s\n'%(actionList,),end='')
                    
                stateCopy = copy.deepcopy(self)
                for action in actionList:
                    func = getattr(stateCopy, action[0])
                    func(*action[1:])

                stateHash = hash(stateCopy)
                if stateHash not in seenStates:
                    seenStates.add(stateHash)

                    stateCopy.bushrots = bushrots
                    stateCopy.drawptrs = drawptrs
                    if successFunction(stateCopy):
                        print('Solved!!!\nSolved!!!\nSolved!!!\n',end='')
                        print('Solved!!!\nSolved!!!\nSolved!!!\n',end='')
                        print('Solved!!!\nSolved!!!\nSolved!!!\n',end='')
                        ret = (stateCopy, actionList)
                        for i in range(num_worker_threads):
                            actionsQueue.put('DONE')
                    else:
                        for action in stateCopy.getAvailableActions(carryingActor):
                            newActionList = actionList + (action,)
                            actionsQueue.put((TupleWrapper(newActionList), stateCopy.bushrots, stateCopy.drawptrs))

                actionsQueue.task_done()

        actionsQueue = queue.PriorityQueue()
        
        threads = []
        for i in range(num_worker_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
            
        actionsQueue.put((TupleWrapper(()), set(), set()))

        for t in threads:
            t.join()

        return ret

    def __str__(self):
        return "\n".join((str(node) for node in self.heap()))

    def __hash__(self):
        stateHash = 0
        for node in self.heap():
            stateHash = hash((stateHash, node.addr, node.description, node.rooms))
        return stateHash

    def __deepcopy__(self, memo):
        selfCopy = copy.copy(self)
        selfCopy.loadedObjects = copy.copy(self.loadedObjects)
        selfCopy.loadedRooms = copy.copy(self.loadedRooms)
        selfCopy.actorStates = copy.deepcopy(self.actorStates)
        selfCopy.ram = {}
        for node in self.heap():
            selfCopy.ram[node.addr] = copy.copy(node)
        selfCopy.bushrots = self.bushrots.copy()
        selfCopy.drawptrs = self.drawptrs.copy()
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

    def __str__(self):
        return "header:%08X data:%08X free:%d blocksize:%X next_addr:%X prev_addr:%X - %s"%(self.addr,self.addr+self.headerSize,self.free,self.blockSize, self.nextNodeAddr, self.prevNodeAddr, self.description)


class TupleWrapper(tuple):
    def __lt__(self, other):
        if random.random() < 0.5:
            return len(self) < len(other)
        else:
            return random.choice([True,False])
    def __le__(self, other):
        if random.random() < 0.5:
            return len(self) <= len(other)
        else:
            return random.choice([True,False])
    def __gt__(self, other):
        if random.random() < 0.5:
            return len(self) > len(other)
        else:
            return random.choice([True,False])
    def __ge__(self, other):
        if random.random() < 0.5:
            return len(self) >= len(other)
        else:
            return random.choice([True,False])


