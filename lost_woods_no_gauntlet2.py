from sim import GameState, actors

state = GameState('OoT', 'OoT-N-1.2', {'lullaby':False, 'saria':False, 'bombchu':False, 'bomb':False, 'bottle':False, 'clearedRooms':[], 'beanPlanted':False, 'switchFlags':[], 'collectibleFlags':[]})

drawPtrs = set()

def move(roomId):
    state.changeRoom(roomId)
    for node in state.heap():
        if node.nodeType == 'INSTANCE' and state.actorDefs[node.actorId]['overlaySize'] and state.actorDefs[node.actorId]['allocType']==0:
            drawPtr = node.addr+state.headerSize+0x134
            ovl = state.actorStates[node.actorId]['loadedOverlay']
            if ovl > drawPtr and ovl > 0x801EC800 and drawPtr < 0x801ECB90:
                drawPtrs.add((ovl, drawPtr, str(node), tuple(state.loadedRooms)))

state.loadScene(sceneId=0x5B, setupId=0, roomId=8)
state.changeRoom(7)
state.changeRoom(4)

move(6)
move(4)
move(6)
move(4)

move(7)
move(8)
move(7)
move(8)
move(7)
move(4)

move(3)
move(2)
move(1)

move(2)
move(3)
move(2)
move(1)

move(2)
move(3)
move(2)
move(1)

move(0)

move(9)
move(5)

move(9)
move(5)

move(9)
move(5)

move(9)
move(0)
move(1)
move(2)
move(3)

move(2)
move(1)
move(2)
move(3)

move(2)
move(1)
move(2)
move(3)



move(2)
move(3)
move(4)
move(6)

move(4)
move(7)
move(8)

#print(state)
#for node in state.heap():
#    if node.actorId:
#        print(node, node.nodeType == 'INSTANCE', state.actorDefs[node.actorId]['drawPtr'], state.actorDefs[node.actorId]['overlaySize'], state.actorDefs[node.actorId]['allocType']==0)

for overlay,ptr,node,rooms in sorted(drawPtrs):
    print(hex(overlay),hex(ptr),node,rooms)
