from sim import GameState, actors
import copy

state = GameState('OoT', 'OoT-J-GC-MQDisc', {'spawnFromGameOver':True,'clearedRooms':[],'bombchu':False,'bomb':True,'bottle':False,'sword':True,'hookshot':False,'boomerang':True,'slingshot':False,'collectibleFlags':[],'switchFlags':[]})
state.loadScene(sceneId=0x55, setupId=0, roomId=0)
mure = state.ram[0x802060A0]
#state.changeRoom(1)
#state.changeRoom(0)
#mure = state.ram[2149611408]
#print(state)
print(sorted(state.getAvailableActions(carryingActor=False,disableInteractionWith={actors.En_Kusa,actors.En_Wonder_Item,actors.En_Wonder_Talk2,actors.En_Item00,actors.En_Ishi},ignoreRooms={1,2})))


actorAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{},0:{}}
actorEndAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{},0:{}}
boomPosAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{},0:{}}
rockBumpAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{},0:{}}
bombExplosionAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{},0:{}}

def cost(actionList):
    cost = 0
    kanban_penalty = 0
    kanban_count = 0
    mure_count = 0
    for a in actionList:
        if a[0] == 'dealloc':
            cost += 1
        elif a[0] == 'allocActor' and a[1] == actors.En_Boom:
            cost += 100
        elif a[0] == 'allocActor' and a[1] == actors.En_Kanban:
            cost += 1
            kanban_count += 1
        elif a[0] == 'allocMultipleActors':
            cost += 1
            mure_count += 1
        else:
            cost += 1
    #if kanban_count > 0:
    #    kanban_penalty = 100
    #    if mure_count == 0:
    #        kanban_penalty = 10000
    return cost + kanban_penalty
        

def check(state, actionList):
    n = mure.childCount
    for node in state.heap():
        if not node.free and node.nodeType=='INSTANCE':
            a = node.addr + state.headerSize + node.blockSize + state.headerSize
            if a not in actorEndAddrs[n] or cost(actionList) < cost(actorEndAddrs[n][a]):
                actorEndAddrs[n][a] = actionList
            if node.actorId in {actors.En_Bom, actors.En_Boom, actors.En_Arrow}:
                a = node.addr + state.headerSize
                if a not in actorAddrs[n] or cost(actionList) < cost(actorAddrs[n][a]):
                    actorAddrs[n][a] = actionList
            if node.actorId == actors.En_Boom:
                a = node.addr + state.headerSize + 0x1AC
                if a not in boomPosAddrs[n] or cost(actionList) < cost(boomPosAddrs[n][a]):
                    boomPosAddrs[n][a] = actionList
            if node.actorId == actors.En_Ishi:
                a2 = node.addr + state.headerSize + 0x188
                if a2 not in rockBumpAddrs[n] or cost(actionList) < cost(rockBumpAddrs[n][a2]):
                    rockBumpAddrs[n][a2] = actionList
            if node.actorId == actors.En_Bom:
                a2 = node.addr + state.headerSize + 0x1D8
                if a2 not in bombExplosionAddrs[n] or cost(actionList) < cost(bombExplosionAddrs[n][a2]):
                    bombExplosionAddrs[n][a2] = actionList


number_of_songs_to_learn = 2
action_limit = 6

most_rocks = 8

for n in reversed(range(0,most_rocks+1)):
    print(n)
    mure.childCount = n
    state.search(check, actionLimit=action_limit, num_worker_threads=1, disableInteractionWith={actors.En_Kusa,actors.En_Wonder_Item,actors.En_Wonder_Talk2,actors.En_Item00,actors.En_Ishi},ignoreRooms={1,2})

number_of_songs_to_learn = 2
for base_rock_count in range(0, most_rocks+1-number_of_songs_to_learn):
    for a1 in sorted(rockBumpAddrs[base_rock_count]):
      if (a1-(0x801fa2e0+0x18))%0x30 in [0,0x10]: # assuming a specific cutscene pointer
        a2 = a1+4
        if a2 in boomPosAddrs[base_rock_count]:
            for i1 in [0xA,0xE,0x12]:
                a3 = a1+8+i1*0xC
                a4 = a3 + 4
                for n in range(base_rock_count+1, most_rocks+1):
                    if a3 in rockBumpAddrs[n] and a4 in boomPosAddrs[n]:
                        for i2 in [0x8,0xC,0x10,0x14]:
                            a5 = a3+i2*0xC
                            a6 = a5 + 4
                            for n2 in range(n+1, most_rocks+1):
                                if a5 in rockBumpAddrs[n2] and a6 in boomPosAddrs[n2]:
                                    a7 = a5 + 0x58
                                    if a7 in actorAddrs[n2]: # should always be true?
                                      total_cost = cost(actorAddrs[n2][a7]) + cost(boomPosAddrs[n2][a6]) + cost(rockBumpAddrs[n2][a5]) + cost(boomPosAddrs[n][a4]) + cost(rockBumpAddrs[n][a3]) + cost(boomPosAddrs[base_rock_count][a2]) + cost(rockBumpAddrs[base_rock_count][a1])
                                      if total_cost < 10000:
                                        print("!")
                                        print(hex(i1+i2+8))
                                        print(hex(a7+0x14), actorAddrs[n2][a7])
                                        print(hex(i1+i2))
                                        print(hex(a6), boomPosAddrs[n2][a6])
                                        print(hex(a5), rockBumpAddrs[n2][a5])
                                        print(hex(i1))
                                        print(hex(a4), boomPosAddrs[n][a4])
                                        print(hex(a3), rockBumpAddrs[n][a3])
                                        print("text_list")
                                        print(hex(a2), boomPosAddrs[base_rock_count][a2])
                                        print(hex(a1), rockBumpAddrs[base_rock_count][a1])
                                        print(total_cost)
                                        #print("csptrs:")
                                        #for a0 in reversed(sorted(actorAddrs[base_rock_count])):
                                        #    if a0 < a1 and (a1-(a0+0x18))%0x30 == 0:
                                        #        i0 = (a1-(a0+0x18)) // 0x30
                                        #        print(hex(i0), hex(a0), actorAddrs[base_rock_count][a0])

print("done")
