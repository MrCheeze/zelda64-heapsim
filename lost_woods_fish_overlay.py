from sim import GameState, actors
import copy

version = 'OoT-N-1.2'

fishAddresses = set()
totalAttempts = 0
def checkFishAddress(state):
    if actors.En_M_Thunder in state.actorStates and state.actorStates[actors.En_M_Thunder]['numLoaded'] > 0:
        return False
    state = copy.deepcopy(state)
    state.allocActor(actors.En_Fish)
    addr = state.actorStates[actors.En_Fish]['loadedOverlay']+state.headerSize
    global totalAttempts
    totalAttempts += 1
    if addr not in fishAddresses:
        print('%08X (%d)\n'%(addr, totalAttempts), end='')
        fishAddresses.add(addr)
    return addr == 0x801F8F30
    #return addr == {'OoT-N-1.0':0x801F8880, 'OoT-N-1.2':0x801F8F30}[version]
    #return addr == {'OoT-N-1.0':0x801F88B0, 'OoT-N-1.2':0x801F8F60}[version]


def ageSrm(state):
    if len(state.loadedRooms) != 1 or 1 not in state.loadedRooms:
        return False
    state = copy.deepcopy(state)
    state.loadRoom(2)
    for node in state.heap():
        '''if node.actorId == actors.En_Kusa and len(state.loadedRooms) == 1:
            addr = node.addr+state.headerSize+0xB4
            if addr == 0x801ed9a4:
                return True
            #state.bushrots.add(addr)'''
        if node.actorId not in [actors.En_Kusa, actors.En_Mm2, actors.Shot_Sun, actors.En_Weather_Tag] and node.actorId in state.actorStates and 'loadedOverlay' in state.actorStates[node.actorId] and state.actorStates[node.actorId]['loadedOverlay'] >= 0x801F0000:
            addr = node.addr+state.headerSize+0x134
            #state.drawptrs.add(addr)
            #if addr in state.bushrots:
            if addr == 0x801ed9a4:
                print(hex(addr))
                return True
    return False

#for j in range(14+1):
# for i in range(7+1):
if True:
    state = GameState('OoT', version, {'adult':True, 'night':False, 'lullaby':False, 'saria':False, 'storms':False, 'bombchu':False, 'bomb':False, 'bottle':False, 'hookshot': False, 'clearedRooms':[], 'beanPlanted':False, 'switchFlags':[], 'collectibleFlags':[]})
    state.loadScene(sceneId=0x5B, roomId=0x2)

    state.changeRoom(1)
    state.loadNeedles(2149462960, (1,))
    state.loadRoom(2)
    state.loadNeedles(2149462960, (2,))
    state.loadNeedles(2149462960, (2,))
    state.unloadRoomsExcept(2)
    state.loadRoom(1)
    state.loadAllNeedles((2,))
    state.unloadRoomsExcept(2)
    state.loadRoom(1)
    state.loadAllNeedles((2,))


    #state.allocMultipleActors(32,3)
    #ret = state.search(checkFishAddress)
    #state.unloadRoomsExcept(1)
    #state.changeRoom(0)

    '''
    state.changeRoom(1)
    state.loadRoom(0)
    for _ in range(j):
        state.allocMultipleActors(actors.En_Skjneedle,3, rooms=(0,))
    state.unloadRoomsExcept(0)
    state.changeRoom(9)
    for _ in range(i):
        state.allocMultipleActors(actors.En_Skjneedle,3)
    state.loadRoom(5)
    for node in state.heap():
        if node.actorId == actors.En_Gs:
            drawptrs.add((state.actorStates[actors.En_Gs]['loadedOverlay'], node.addr+state.headerSize+0x134, j, i))
    '''
    
    '''
    state.changeRoom(1)
    for _ in range(i):
        state.allocMultipleActors(actors.En_Skjneedle,3)
    state.allocActor(actors.En_Bom)
    state.loadRoom(2)
    for node in state.heap():
        addr = node.addr+state.headerSize+0xB4
        if node.actorId == actors.En_Kusa and addr in good_drawptrs:
            print(i, hex(addr))
    '''

    state.unloadRoomsExcept(1)
    state.loadRoom(2)
    state.loadNeedles(2149462960, (2,))
    state.loadNeedles(2149462960, (2,))
    state.loadNeedles(2149462960, (1,))
    state.unloadRoomsExcept(1)
    state.changeRoom(2)
    state.changeRoom(1)

    state.loadNeedles(2149485408, (1,))
    #state.loadRoom(2)
    
    
    state.bushrots = set()
    state.drawptrs = set()
    #print(state)
    #1/0
    ret = state.search(ageSrm, carryingActor=True)
    print(ret)

#for x in sorted(drawptrs):
#    print(hex(x[0]),hex(x[1]), x)
