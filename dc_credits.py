from sim import GameState, actors
import copy

state = GameState('OoT', 'OoT-N-1.0', {'lullaby':False, 'saria':False, 'bombchu':True, 'bomb':False, 'bottle':False, 'clearedRooms':[], 'beanPlanted':False, 'collectibleFlags':[], 'switchFlags':[], 'sword':False})
state.loadScene(sceneId=1, setupId=0, roomId=7)

potAngles = {}

printed = set()

editable_overlays = {
'Overlay 0125 En_Kusa':      '0291 V00E02650 ovl_En_Kusa.actor',
'Overlay 0059 Bg_Breakwall': '0107 V00C9E810 ovl_Bg_Breakwall.actor',
'Overlay 012A Obj_Switch':   '0294 V00E06830 ovl_Obj_Switch.actor',
'Overlay 0013 En_Firefly':   '0047 V00C13AA0 ovl_En_Firefly.actor',
}

def is_branch_instruction(instr):
    if 0x1000 < (instr % 0x10000) < 0xF000:
        return False
    assert 0 <= instr < 0x100000000
    if (0x10000000 <= instr < 0x20000000) or (0x50000000 <= instr < 0x60000000):
        return True
    elif (0x04000000 <= instr < 0x08000000):
        sub_instr = instr % 0x200000
        return (0x000000 <= sub_instr < 0x040000) or (0x100000 <= sub_instr < 0x140000)
    else:
        return (0x0C070000 <= instr < 0x0C080000)
    #return (0x0C070000 <= instr < 0x10000000) or (False and 0x80000000 <= instr < 0x80400000)

for k in editable_overlays:
    editable_overlays[k] = open('sim/roms/Zelda no Densetsu - Toki no Ocarina (J) (V1.2)/'+editable_overlays[k],'rb').read()
    for offset in range(4, len(editable_overlays[k]), 0x10):
        value = int.from_bytes(editable_overlays[k][offset:offset+4], 'big')
        if is_branch_instruction(value):
            print('%s %X - %08X'%(k, 0+offset, value))

def isPrefixOf(tuple1, tuple2):
    return len(tuple1) <= len(tuple2) and tuple1 == tuple2[0:len(tuple1)]

def isGood(actionList):
    for action in actionList:
        if action[0] in ['dealloc', 'allocActor']:
            return False
    return True

blacklist = {
    ('Overlay 012A Obj_Switch', 0x574),
    ('Overlay 012A Obj_Switch', 0x1484),
    ('Overlay 0059 Bg_Breakwall', 0xB4),
    ('Overlay 012A Obj_Switch', 0x614),
}

branch_instrs = {
    'Overlay 0125 En_Kusa': {
        0x564, # 562AFF68
    },
    'Overlay 0059 Bg_Breakwall': {
        0x394, # 1020FFE2
        0x644, # 0581FF83
        0xAD4, # 5653FFFA
    },
}

overlayAddrs = set()

def add(addr):
    if addr not in overlayAddrs:
        print(hex(addr)+'\n',end='')
        overlayAddrs.add(addr)

def checkPots(state, actionList):
    for node in state.heap():
        if not node.free and node.nodeType!='INSTANCE':
            for addr in copy.copy(potAngles):
                if node.addr+state.headerSize <= addr < node.addr+state.headerSize+node.blockSize and 'En_Bom_Chu' not in node.description:
                    s=node.description
                    if s not in printed:
                        print(s+'\n',end='')
                        printed.add(s)
                    
        '''
        if not node.free and node.nodeType!='INSTANCE':
            potAnglesCopy = copy.copy(potAngles)
            for addr in potAnglesCopy:
                for actionListPrefix in copy.copy(potAnglesCopy[addr]):
                    if isPrefixOf(actionListPrefix, actionList):
                        if node.addr+state.headerSize <= addr < node.addr+state.headerSize+node.blockSize and 'En_Bom_Chu' not in node.description:
                            offset = addr-node.addr-state.headerSize
                            value = int.from_bytes(editable_overlays[node.description][offset:offset+4], 'big')
                            s = '%08X = "%s" + %X - %08X'%(addr, node, offset, value)
                            actionListSuffix = actionList[len(actionListPrefix):]
                            if is_branch_instruction(value) and s not in printed and (node.description,offset) not in blacklist and isGood(actionListSuffix):
                                print(actionListPrefix)
                                print(actionListSuffix)
                                print(s)
                                printed.add(s)
                                return True
        if node.description in branch_instrs:
            potAnglesCopy = copy.copy(potAngles)
            for addr in copy.copy(potAnglesCopy):
                offset = addr-node.addr-state.headerSize
                if offset in branch_instrs[node.description]:
                    #for actionListPrefix in copy.copy(potAnglesCopy[addr]):
                    #    if isPrefixOf(actionListPrefix, actionList):
                    #        actionListSuffix = actionList[len(actionListPrefix):]
                    #        if isGood(actionListSuffix):
                                s = '%08X = "%s" + %X'%(addr, node, offset)
                                if True or s not in printed:
                                    print(s+'\n', end='')
                                    printed.add(s)
                                    #return True
        '''
        if not node.free and node.nodeType=='INSTANCE' and ('unloadRoomsExcept', 8) in actionList:
            if node.actorId == actors.Obj_Tsubo:
                angle = node.addr+state.headerSize+0xB4
                if angle not in potAngles:
                    #print('angle %08X %04X\n'%(angle, node.actorId),end='')
                    potAngles[angle] = set()
                    #if angle in {0x801e2db4,0x801ecbc4,0x801ece74,0x801ed304,0x801ec8c4,0x801ecb74,0x801ed004,0x801ebb04,0x801ebdb4,0x801ec244}:
                    #    return True
                potAngles[angle].add(actionList)
            #draw = node.addr+state.headerSize+0x134
            #if draw in potAngles:
            #    print('draw %08X %04X\n'%(draw, node.actorId),end='')
            #    return True
    '''
    if state.actorStates[actors.En_Kusa]['numLoaded']:
        add(state.actorStates[actors.En_Kusa]['loadedOverlay']+state.headerSize+0x564)
    if actors.Bg_Breakwall in state.actorStates and state.actorStates[actors.Bg_Breakwall]['numLoaded']:
        add(state.actorStates[actors.Bg_Breakwall]['loadedOverlay']+state.headerSize+0x394)
        add(state.actorStates[actors.Bg_Breakwall]['loadedOverlay']+state.headerSize+0x644)
        add(state.actorStates[actors.Bg_Breakwall]['loadedOverlay']+state.headerSize+0xAD4)
    '''
    #return False

#print(state.ram[2149474448])
#print(state.ram[2149475376])
#print(state.ram[2149465392])
#ret = state.search(checkPots, carryingActor=False, disableInteractionWith=[actors.Door_Shutter])

#print(ret)

state.changeRoom(8)
state.changeRoom(7)
state.changeRoom(8)
state.changeRoom(7)

for node in state.heap():
    if not node.free and node.nodeType=='INSTANCE':
        if node.actorId == actors.Obj_Tsubo:
            angle = node.addr+state.headerSize+0xB4
            print('angle %08X %04X\n'%(angle, node.actorId),end='')
            potAngles[angle] = set()
        if node.actorId == actors.En_Firefly:
            state.dealloc(node.addr)

state.changeRoom(8)

#print(state)
for angle in potAngles:
    print(hex(angle - state.actorStates[actors.En_Firefly]['loadedOverlay'] - state.headerSize))
