from sim import GameState, actors
import copy

version = 'OoT-N-1.2'

afc_actors = {
    actors.En_Sw: [0x80948B2C-0x80945770],
    actors.En_Skj: [0x80A6FE00-0x80A6CA90],
    actors.En_Hs: [0x80AA16E0-0x80AA0C70],
    actors.En_Ko: [0x80AD5590-0x80AD1C20,0x80AD55C4-0x80AD1C20,0x80AD55F8-0x80AD1C20,0x80AD5634-0x80AD1C20,0x80AD565C-0x80AD1C20,0x80AD5690-0x80AD1C20,0x80AD56C4-0x80AD1C20,0x80AD56F8-0x80AD1C20,0x80AD572C-0x80AD1C20,0x80AD5760-0x80AD1C20,0x80AD5780-0x80AD1C20],
    actors.En_Weather_Tag: [0x80AD7FB0-0x80AD7270],
    actors.En_Md: [0x80AE4AC0-0x80AE2870,0x80AE4AEC-0x80AE2870,0x80AE4B4C-0x80AE2870],
    actors.En_Gs: [0x80B6DC34-0x80B6C070],
}

filename_addrs = {'OoT-N-1.0':[0x8011A5F4,0x8011A5F8],
                  'OoT-N-1.1':[0x8011A7B4,0x8011A7B8],
                  'OoT-N-1.2':[0x8011ACA4,0x8011ACA8]}

controller_addrs = {'OoT-N-1.0':[0x8011D730,0x8011D760,0x8011D790,0x8011D79C],
                    'OoT-N-1.2':[0x8011DE00,0x8011DE30,0x8011DE60,0x8011DE6C]}

def checkFunctionOverlays(state):
    state = copy.deepcopy(state)
    #if len(state.loadedRooms) != 1 or 4 not in state.loadedRooms:
    #    return False
    #state.loadRoom(3)
    for act in afc_actors:
        if act in state.actorStates:
            for offset in afc_actors[act]:
                if offset % 0x10 in [0x0,0xC]:
                    addr = state.actorStates[act]['loadedOverlay']+state.headerSize+offset
                    for faddr in controller_addrs[version]:
                        if faddr%0x10000 == addr % 0x10000:
                            print('%X %08X %08X\n'%(act,addr,faddr),end='')
                            print(str(state)+'\n',end='')
                            return True
    return False

bush_rots = set()

def checkBushRots(state):
    for node in state.heap():
        if node.actorId == actors.En_Kusa:
            addr = node.addr+state.headerSize+0xB4
            #if addr not in bush_rots and addr >= 0x801E3074 and addr <= 0x801ECF14:
            if addr in [0x801E3074,0x801E31E4,0x801E3404,0x801E3574,0x801E35C4,0x801E3734,0x801E3784,0x801EA1D4,0x801EA394,0x801EA934,0x801EAAF4,0x801EC814,0x801EC9D4,0x801ECB94,0x801ECD54,0x801ECF14]:
                bush_rots.add(addr)
                print(hex(addr))
                return list(state.heap())[-1].addr < 0x801ED17C

state = GameState('OoT', version, {'lullaby':False, 'saria':False, 'bombchu':False, 'bomb':True, 'bottle':False, 'hookshot': False, 'clearedRooms':[], 'beanPlanted':False, 'switchFlags':[], 'collectibleFlags':[]})
state.loadScene(sceneId=0x5B, setupId=2, roomId=3)
state.changeRoom(4)
state.loadRoom(7)
b1=state.allocActor(actors.En_Bom)
b2=state.allocActor(actors.En_Bom)
state.unloadRoomsExcept(4)
b3=state.allocActor(actors.En_Bom)
state.loadRoom(3)
state.dealloc(b1.addr)
state.dealloc(b2.addr)
state.dealloc(b3.addr)


#state.changeRoom(7)
#state.loadRoom(8)
#(<sim.sim.GameState object at 0x06C47C50>, (['allocActor', 16], ['allocActor', 16], ['allocActor', 16], ['unloadRoomsExcept', 4], ['loadRoom', 7], ['unloadRoomsExcept', 7], ['loadRoom', 8]))



ret = state.search(checkBushRots)
print(ret)
print(ret[0])
