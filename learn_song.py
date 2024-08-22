from sim import GameState, actors
import copy

state = GameState('OoT', 'OoT-J-GC-MQDisc', {'spawnFromGameOver':False,'clearedRooms':[],'bombchu':False,'bomb':True,'bottle':False,'sword':True,'hookshot':False,'boomerang':True,'slingshot':False})
state.loadScene(sceneId=0x47, setupId=0, roomId=0)
mure = state.allocActor(actors.Obj_Mure2, {0}, 0x0202)
state.initFunction(mure, True)
ishi1 = state.allocActor(actors.En_Ishi, {0})
ishi2 = state.allocActor(actors.En_Ishi, {0})
state.dealloc(ishi1.addr)


actorAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{}}
actorEndAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{}}
boomPosAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{}}
rockBumpAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{}}
bombExplosionAddrs = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{}}

def check(state, actionList):
    n = mure.childCount
    for node in state.heap():
        if not node.free and node.nodeType=='INSTANCE' and node.addr > mure.addr:
            a = node.addr + state.headerSize + node.blockSize + state.headerSize -0x801F1680+0x213F30
            if a not in actorEndAddrs[n] or len(actionList) <= len(actorEndAddrs[n][a]):
                actorEndAddrs[n][a] = actionList
            if node.actorId in {actors.En_Bom, actors.En_Boom, actors.En_Arrow}:
                a = node.addr + state.headerSize -0x801F1680+0x213F30
                if a not in actorAddrs[n] or len(actionList) < len(actorAddrs[n][a]):
                    actorAddrs[n][a] = actionList
            if node.actorId == actors.En_Boom:
                a = node.addr + state.headerSize + 0x1AC -0x801F1680+0x213F30
                if a not in boomPosAddrs[n] or len(boomPosAddrs) < len(boomPosAddrs[n][a]):
                    boomPosAddrs[n][a] = actionList
            if node.actorId == actors.En_Ishi:
                a2 = node.addr + state.headerSize + 0x188 -0x801F1680+0x213F30
                if a2 not in rockBumpAddrs[n] or len(actionList) < len(rockBumpAddrs[n][a2]):
                    rockBumpAddrs[n][a2] = actionList
            if node.actorId == actors.En_Bom:
                a2 = node.addr + state.headerSize + 0x1D8 -0x801F1680+0x213F30
                if a2 not in bombExplosionAddrs[n] or len(actionList) < len(bombExplosionAddrs[n][a2]):
                    bombExplosionAddrs[n][a2] = actionList


number_of_songs_to_learn = 2
action_limit = 6

most_rocks = 8

for n in reversed(range(2,most_rocks+1)):
    print(n)
    mure.childCount = n
    state.search(check, actionLimit=action_limit, num_worker_threads=1, disableInteractionWithAddrs={ishi2.addr}, disableInteractionWith={actors.En_Ishi})

'''
for base_rock_count in range(2, most_rocks-number_of_songs_to_learn+1):
#  if base_rock_count == most_rocks-number_of_songs_to_learn: # temp deleteme
    for a in sorted(rockBumpAddrs[base_rock_count]):
        a0 = a+4
        if a0 in boomPosAddrs[base_rock_count]:
            s = hex(a0) + " " + str(boomPosAddrs[base_rock_count][a0]) + "\n"
            s += hex(a) + " " + str(rockBumpAddrs[base_rock_count][a]) + "\n"
            count_m1 = 0
            s_m1 = ""
            for a_m1 in [a_m1 for a_m1 in reversed(sorted(actorAddrs[base_rock_count])) if (a_m1+0x18) <= a]:
                if (a-(a_m1+0x18))%0x30 == 0:
                    i_m1 = (a-(a_m1+0x18)) // 0x30
                    s_m1 += hex(i_m1) + ":\n"
                    s_m1 += hex(a_m1) + " " + str(actorAddrs[base_rock_count][a_m1]) + "\n"
                    count_m1 += 1
            if count_m1 == 0:
                continue
            count4 = 0
            s4 = ""
            s4_ = {}
            max_i5 = -1
            for a4 in [a4 for a4 in reversed(sorted(actorAddrs[most_rocks])) if (a4+0x40) >= a + 8]: # should this most_rocks be hardcoded? seems wrong
                for offset in [0x40,0x38,0x30,0x2C,0x28,0x24,0x20,0x1C,0x14,0x10,0xC,0x8,0x4]:
                    a5 = a4 + offset
                    if a5 >= a+8 and (a5-(a+8))%0xC == 0:
                        i5 = (a5-(a+8)) // 0xC
                        if i5 < 0x2A: # temp deleteme
                            s4 += hex(i5) + ":\n"
                            s4 += hex(a5) + " " + str(actorAddrs[most_rocks][a4]) + "\n" # above
                            count4 += 1
                            s4_[i5] = s4 + "^^^ "+str(count4)+" ^^^\n"
                            max_i5 = max(i5, max_i5)
            if count4 == 0:
                continue
            i_must_be_less_than = max_i5-7
            count_ = 0
            s2__ = {8:{},7:{},6:{},5:{},4:{},3:{},2:{},1:{}}
            highest = None
            for n in reversed(range(base_rock_count+1,most_rocks+1)):
                count = 0
                max_i = -1
                for a2 in [a2 for a2 in reversed(sorted(rockBumpAddrs[n])) if a2 >= a + 8 and a2+4 in boomPosAddrs[n]]:
                    a3 = a2 + 4
                    if (a2-(a+8))%0xC == 0:
                        i = (a2-(a+8)) // 0xC
                        if i < i_must_be_less_than:
                            s2_ = hex(i) + " ("+str(n)+"):\n"
                            s2_ += hex(a3) + " " + str(boomPosAddrs[n][a3]) + "\n"
                            s2_ += hex(a2) + " " + str(rockBumpAddrs[n][a2]) + "\n"
                            s2__[n][i] = s2_
                            count += 1
                            if highest is None:
                                highest = n
                            max_i = max(i, max_i)
                if count > 0:
                    i_must_be_less_than = max_i-7
                    count_ += 1
            if count_ < number_of_songs_to_learn:
                continue
            #wrong
            #for n in range(base_rock_count+2,8+1):
            #    for k in list(s2__[n]):
            #        if k <= 7+min(s2__[n-1].keys()):
            #            del s2__[n][k]
            s2 = ""
            for n in reversed(range(2,most_rocks+1)):
                for i in reversed(sorted(s2__[n])):
                    s2 += s2__[n][i]
            print(s4_[min([k for k in s4_ if k > 7+min(s2__[highest].keys())])] + s2 + "^^^ "+str(count_)+" ^^^\n" + s + "vvv "+str(count_m1)+" vvv\n" + s_m1 + "-"*70)
'''

number_of_songs_to_learn = 2
for base_rock_count in range(2, most_rocks+1-number_of_songs_to_learn):
    for a1 in sorted(rockBumpAddrs[base_rock_count]):
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
                                        total_cost = len(actorAddrs[n2][a7]) + len(boomPosAddrs[n2][a6]) + len(rockBumpAddrs[n2][a5]) + len(boomPosAddrs[n][a4]) + len(rockBumpAddrs[n][a3]) + len(boomPosAddrs[base_rock_count][a2]) + len(rockBumpAddrs[base_rock_count][a1])
                                        print(total_cost)
                                        print("csptrs:")
                                        for a0 in reversed(sorted(actorAddrs[base_rock_count])):
                                            if a0 < a1 and (a1-(a0+0x18))%0x30 == 0:
                                                i0 = (a1-(a0+0x18)) // 0x30
                                                print(hex(i0), hex(a0), actorAddrs[base_rock_count][a0])

print("done")

'''
for a in sorted(actorEndAddrs[6]):
    print(hex(a), actorEndAddrs[6][a])
'''
