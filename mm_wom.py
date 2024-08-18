from sim import GameState, mmactors
import copy

'''
state = GameState('MM', 'MM-J-1.1', {'clearedRooms':[]})
state.loadScene(sceneId=0x64, setupId=0, roomId=1, dayNumber=4)

grottos = set()

def checkGrottos(state, actionList):
    if mmactors.Door_Ana in state.actorStates and 'loadedOverlay' in state.actorStates[mmactors.Door_Ana]:
        addr = state.actorStates[mmactors.Door_Ana]['loadedOverlay']+state.headerSize + 0x5F4
        if addr not in grottos:
            grottos.add(addr)
            print(hex(addr)+' '+str(actionList)+'\n',end='')
    return False

state.search(successFunction=checkGrottos, actionLimit=7, carryingActor=True)

print("------------")
'''

state = GameState('MM', 'MM-J-1.1', {'clearedRooms':[]})
state.loadScene(sceneId=0x64, setupId=0, roomId=1, dayNumber=4)

totalActionLimit = 12

def checkBushes(state, actionList):
    if len(state.loadedRooms) == 1 and 4 in state.loadedRooms:
        bushAddrs = set()
        for node in state.heap():
            if not node.free and node.nodeType=='INSTANCE' and node.actorId == mmactors.En_Kusa:
                addr = node.addr + state.headerSize + 0x24
                bushAddrs.add(addr)
        if len(bushAddrs) > 0:

            def checkGrottos(state, actionList2):
                if mmactors.Door_Ana in state.actorStates and 'loadedOverlay' in state.actorStates[mmactors.Door_Ana]:
                    addr = state.actorStates[mmactors.Door_Ana]['loadedOverlay']+state.headerSize + 0x5F4
                    if addr in bushAddrs:
                        print(hex(addr)+' '+str(actionList)+' '+str(actionList2)+'\n',end='')
            
            state.search(successFunction=checkGrottos, actionLimit=totalActionLimit-len(actionList), carryingActor=True, printProgress=False)

state.search(successFunction=checkBushes, actionLimit=(totalActionLimit-2), carryingActor=False)
