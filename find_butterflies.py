from sim import GameState, actors

for sceneId in range(0x70):
    for roomId in range(0x20):
        state = GameState('OoT', 'OoT-N-1.2', {'adult':True,'night':False,'lullaby':False, 'saria':False, 'bombchu':False, 'bomb':False, 'bottle':False, 'clearedRooms':[], 'beanPlanted':False, 'switchFlags':[], 'collectibleFlags':[]})
        try:
            state.loadScene(sceneId=sceneId, roomId=roomId)
        except IndexError:
            break
        state.allocActor(actors.En_Bom_Chu)
        #state.allocActor(actors.En_Fish)
        state.allocActor(actors.En_Insect)
        state.allocActor(actors.En_Insect)
        state.allocActor(actors.En_Insect)
        for node in state.heap():
            if node.actorId == actors.Obj_Mure and node.actorParams&0x001F == 0x0004:
                state.allocActor(actors.En_Butte)
                print(hex(sceneId), hex(roomId), node, hex(state.actorStates[actors.En_Butte]['loadedOverlay']))
                #print(state)

#state = GameState('OoT', 'OoT-N-1.2', {'lullaby':False, 'saria':False, 'bombchu':False, 'bomb':False, 'bottle':False, 'clearedRooms':[], 'beanPlanted':False, 'switchFlags':[], 'collectibleFlags':[]})
#state.loadScene(sceneId=0x59, setupId=0, roomId=0)
#print(state)
