from sim import GameState, actors
import copy

version = 'OoT-N-1.2'

bushes = set()

def checkBushes(state):
    for node in state.heap():
        if node.actorId == actors.En_Kusa:
            addr = node.addr + state.headerSize
            if addr == 0x801E3690:
                return True
            elif addr not in bushes:
                #print(hex(addr))
                bushes.add(addr)
    return False

state = GameState('OoT', version, {'lullaby':False, 'saria':False, 'storms': True, 'bombchu':False, 'bomb':True, 'bottle':False, 'hookshot': False, 'clearedRooms':[], 'beanPlanted':False, 'switchFlags':[], 'collectibleFlags':[]})
state.loadScene(sceneId=0x5B, setupId=2, roomId=8)
print(state)


ret = state.search(checkBushes)
print(ret)
print(ret[0])
