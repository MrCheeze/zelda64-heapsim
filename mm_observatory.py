from sim import GameState, mmactors
import copy

state = GameState('MM', 'MM-J-1.0', {'clearedRooms':[],'sword':False,'magic':True,'bomb':True})
state.loadScene(sceneId=0x29, setupId=0, roomId=1, dayNumber=3)

#state.dealloc(2151771584)
#state.dealloc(2151771120)
#state.dealloc(2151770656)
#state.allocActor(9, held=True)
#state.changeRoom(0)
#state.explode(2151761568, 0)
#state.changeRoom(1)
#state.allocActor(9, held=True)
#state.drop(2151724848, 1)
#state.allocActor(9, held=True)
#state.changeRoom(0)
#state.explode(2151725424, 0)
#state.allocActor(9, held=True)
#state.drop(2151724848, 0)
#state.allocActor(9, held=True)
#state.drop(2151725424, 0)
#state.allocActor(9, held=True)
#state.drop(2151736672, 0)
#state.changeRoom(1)

'''
state.allocActor(9)
state.explode(2151724848, 1)
state.loadRoom(0)
state.unloadRoomsExcept(0)
state.loadRoom(1)
state.unloadRoomsExcept(1)
'''
print(state)
print(state.getAvailableActions(carryingActor=False))

def check(state_, actionList):
    if len(state_.loadedRooms) == 1 and 0 in state_.loadedRooms:
        state = copy.deepcopy(state_)
        state.changeRoom(1)
        for node in list(state.heap()):
            if not node.free and node.nodeType=='INSTANCE':
                if node.actorId in [mmactors.En_Clear_Tag, mmactors.En_Bom, mmactors.En_M_Thunder]:
                    state.dealloc(node.addr)
        potAddrs = set()
        for node in state.heap():
            if not node.free and node.nodeType=='INSTANCE' and node.actorId == mmactors.Obj_Tsubo:
                addr = node.addr + state.headerSize + 0xBC
                potAddrs.add(addr)
        if len(potAddrs) > 0:
            state2 = copy.deepcopy(state)
            bomb = state2.allocActor(9)
            state2.explode(bomb.addr, 1)
            for i in range(3):
                state2.loadRoom(0)
                state2.unloadRoomsExcept(0)
                state2.loadRoom(1)
                state2.unloadRoomsExcept(1)
                for node in state2.heap():
                    if not node.free and node.nodeType=='INSTANCE' and 'loadedOverlay' in state2.actorStates[node.actorId] and state2.actorStates[node.actorId]['loadedOverlay'] < 0x80410000:
                        addr = node.addr + state2.headerSize + 0x13C
                        if addr in potAddrs:
                            print(hex(addr)+' '+str(actionList)+' '+'En_Clear_Tag'+str(i)+' '+node.description+' '+hex(state2.actorStates[node.actorId]['loadedOverlay'])+'\n',end='')
                            break
                            #return True
                    
            state2 = state
            for i in range(3):
                state2.loadRoom(0)
                state2.unloadRoomsExcept(0)
                state2.loadRoom(1)
                state2.unloadRoomsExcept(1)
                for node in state2.heap():
                    if not node.free and node.nodeType=='INSTANCE' and 'loadedOverlay' in state2.actorStates[node.actorId] and state2.actorStates[node.actorId]['loadedOverlay'] < 0x80410000:
                        addr = node.addr + state2.headerSize + 0x13C
                        if addr in potAddrs:
                            print(hex(addr)+' '+str(actionList)+' '+str(i)+' '+node.description+' '+hex(state2.actorStates[node.actorId]['loadedOverlay'])+'\n',end='')
                            break
                            #return True

state.search(successFunction=check, actionLimit=12, carryingActor=False)
