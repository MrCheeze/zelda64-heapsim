####doesn't work

from sim import GameState, actors
import copy

results = set()
def checkDrawPointers(state):

    for node in state.heap():
        if node.addr >= 0x801EC000:
            break
        #if node.actorId and node.actorId not in [actors.En_Dnt_Nomal, actors.En_Kusa, actors.En_Wonder_Item] and not (node.actorId==actors.En_Skj and node.actorParams==0x1BFF) and 'loadedOverlay' in state.actors[node.actorId] and state.actors[node.actorId]['loadedOverlay'] >= 0x801EF320:
        if node.actorId and node.actorId in [actors.En_Kusa] and 'loadedOverlay' in state.actorStates[node.actorId] and state.actorStates[node.actorId]['loadedOverlay'] >= 0x801EF320 and 2 not in state.loadedRooms:
            results.add((str(node), str(state.ram[state.actorStates[node.actorId]['loadedOverlay']])))
            #print('!!!')
            return True
    return False


    
    #if 'loadedOverlay' not in state.actors[actors.En_Fish]:
    #    state = copy.deepcopy(state)
    #    state.allocActor(actors.En_Fish)
    #addr = state.actors[actors.En_Fish]['loadedOverlay']+state.headerSize
    #if addr not in fishAddresses:
    #    print(hex(addr))
    #    fishAddresses.add(addr)
    #return False#return addr == 0x801F8F30


#print(state)

if True:
 #for j in ['nut','butte','nutbutte','buttenut']:
  #for switchFlags in [[0x1E],[0x1E],[0x1E],[0x1E]]:

    #print(i, j)

    state = GameState('OoT', 'OoT-N-1.2', {'lullaby':False, 'saria':False, 'bombchu':False, 'bomb':False, 'bottle':False, 'clearedRooms':[], 'beanPlanted':False, 'switchFlags':[0x1E], 'collectibleFlags':[]})
    #state = GameState('OoT', 'OoT-N-1.2', {'lullaby':False, 'saria':False, 'bombchu':False, 'bomb':False, 'bottle':False, 'clearedRooms':[], 'beanPlanted':False, 'switchFlags':[0x11,0x1E,0x1F], 'collectibleFlags':[0x13]})


    #state.loadScene(sceneId=0x5B, setupId=0, roomId=0)
    #state.changeRoom(1)
    #state.changeRoom(2)
    #state.changeRoom(3)
    #state.changeRoom(4)

    state.loadScene(sceneId=0x5B, setupId=0, roomId=6)
    state.changeRoom(4)

    #state.loadScene(sceneId=0x5B, setupId=0, roomId=8)
    
    state.changeRoom(7)
    
    state.changeRoom(4)
    state.changeRoom(3)
    
    state.changeRoom(4)
    state.changeRoom(6)

    j = 'buttenut'
    
    if j == 'nut':
        state.allocActor(actors.En_Nutsball, rooms=[6])
    if j == 'butte':
        state.allocActor(actors.En_Butte, rooms=[6])
        state.allocActor(actors.En_Butte, rooms=[6])
        state.allocActor(actors.En_Butte, rooms=[6])
    if j == 'nutbutte':
        state.allocActor(actors.En_Nutsball, rooms=[6])
        state.allocActor(actors.En_Butte, rooms=[6])
        state.allocActor(actors.En_Butte, rooms=[6])
        state.allocActor(actors.En_Butte, rooms=[6])
    if j == 'buttenut':
        state.allocActor(actors.En_Butte, rooms=[6])
        state.allocActor(actors.En_Butte, rooms=[6])
        state.allocActor(actors.En_Butte, rooms=[6])
        state.allocActor(actors.En_Nutsball, rooms=[6])
    

    
    ret = state.search(checkDrawPointers, carryingActor=True)
    print(ret)
    #print(results)
    if (ret):
        print(results)
        print(i, j)
