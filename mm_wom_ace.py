from sim import GameState, mmactors
import copy

state = GameState('MM', 'MM-J-1.0', {'clearedRooms':[],'sword':True,'magic':True})
state.loadScene(sceneId=0x64, setupId=0, roomId=1, dayNumber=3)
#print(state)
#print(state.getAvailableActions(carryingActor=False))

totalActionLimit = 18

def checkBushes(state, actionList):
    if len(state.loadedRooms) == 1 and next(iter(state.loadedRooms)) in (4,7):
        bushAddrs = set()
        for node in state.heap():
            if not node.free and node.nodeType=='INSTANCE' and node.actorId == mmactors.En_Kusa:
                addr = node.addr + state.headerSize + 0xBC
                bushAddrs.add(addr)
        if len(bushAddrs) > 0:
            def checkDrawPointers(state2, actionList2):
                for node in state2.heap():
                    if not node.free and node.nodeType=='INSTANCE' and node.actorId not in [mmactors.Obj_Etcetera,mmactors.Obj_Kinoko] and 'loadedOverlay' in state2.actorStates[node.actorId] and state2.actorStates[node.actorId]['loadedOverlay'] < 0x80410000:
                        if node.actorId == mmactors.En_Kusa and state2.actorStates[node.actorId]['loadedOverlay'] >= 0x8040E59C:
                            continue
                        addr = node.addr + state2.headerSize + 0x13C
                        if addr in bushAddrs:
                            print(hex(addr)+' '+str(actionList)+' '+str(actionList2)+' '+node.description+' '+hex(state2.actorStates[node.actorId]['loadedOverlay'])+'\n',end='')
            
            state.search(successFunction=checkDrawPointers, actionLimit=totalActionLimit-len(actionList), carryingActor=True, printProgress=False)

state.search(successFunction=checkBushes, actionLimit=(totalActionLimit-2), carryingActor=False)
        
