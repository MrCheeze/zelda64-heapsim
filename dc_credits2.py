from sim import GameState, actors
import copy

state = GameState('OoT', 'OoT-N-1.0', {'lullaby':False, 'saria':False, 'bombchu':True, 'bomb':False, 'bottle':False, 'clearedRooms':[], 'beanPlanted':False, 'collectibleFlags':[], 'switchFlags':[], 'sword':False})
state.loadScene(sceneId=1, setupId=0, roomId=0)

potAddrs = set()

def checkHeap():
    for node in state.heap():
        for addr in potAddrs:
            if not node.free and (node.addr+state.headerSize <= addr < node.addr+state.headerSize+node.blockSize):
                offset = addr-node.addr-state.headerSize
                if node.nodeType == 'INSTANCE' and offset == 0x134:
                    print(hex(addr), node.description, '%X'%(offset))
                #if node.nodeType != 'INSTANCE':
                #    print(hex(addr), node.description, '%X'%(offset))

for i in range(10):
    print('-',i,'-')
    state.changeRoom(1)
    j = 0
    k = 0
    checkHeap()
    for node in state.heap():
        if node.actorId == actors.Obj_Tsubo:
            addr = node.addr+state.headerSize+0xB4
            if j < 4 and addr not in potAddrs:
                print(hex(addr))
                potAddrs.add(addr)
            j += 1
        if i == 3 and node.actorId == actors.En_Dodojr and k < 3:
            state.dealloc(node.addr)
            k += 1
    print()
    state.changeRoom(0)
    checkHeap()
