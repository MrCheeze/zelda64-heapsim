import struct
import json
import pprint

versions = [
    {'name':"OoT-N-1.0",'filename':'Zelda no Densetsu - Toki no Ocarina (J) (V1.0).dec','actortable':0xB5E490,'scenetable':0xB71440,'heapStart':0x801DAA00,'console':'N64','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-N-1.1",'filename':'Zelda no Densetsu - Toki no Ocarina (J) (V1.1).dec','actortable':0xB5E650,'scenetable':0xB71600,'heapStart':0x801DABC0,'console':'N64','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-P-1.0",'filename':'Legend of Zelda, The - Ocarina of Time (PAL) (V1.0).dec','actortable':0xB5DDA0,'scenetable':0xB70D60,'heapStart':0x801D8A40,'console':'N64','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-N-1.2",'filename':'Zelda no Densetsu - Toki no Ocarina (J) (V1.2).dec','actortable':0xB5E490,'scenetable':0xB71450,'heapStart':0x801DB2C0,'console':'N64','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-P-1.1",'filename':'Legend of Zelda, The - Ocarina of Time (PAL) (V1.1).dec','actortable':0xB5DDE0,'scenetable':0xB70DA0,'heapStart':0x801D8A80,'console':'N64','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-J-GC-MQDisc",'filename':'Zelda no Densetsu - Toki no Ocarina (J) (GC) [MQ Disc].dec','actortable':0xB5CB60,'scenetable':0xB6FB20,'heapStart':0x801DBBA0,'console':'GC','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-J-MQ",'filename':'Zelda no Densetsu - Toki no Ocarina Ura (J) (GC).dec','actortable':0xB5CB40,'scenetable':0xB6FB00,'heapStart':0x801DBBA0,'console':'GC','game':'OoT', 'variation':'MQ'},
    {'name':"OoT-U-GC",'filename':'Legend of Zelda, The - Ocarina of Time (U) (GC).dec','actortable':0xB5CB40,'scenetable':0xB6FB00,'heapStart':0x801DBBA0,'console':'GC','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-U-MQ",'filename':'Legend of Zelda, The - Ocarina of Time - Master Quest (U) (GC).dec','actortable':0xB5CB20,'scenetable':0xB6FAE0,'heapStart':0x801DBB60,'console':'GC','game':'OoT', 'variation':'MQ'},
    {'name':"OoT-P-GC",'filename':'Legend of Zelda, The - Ocarina of Time (PAL) (GC).dec','actortable':0xB5C4A0,'scenetable':0xB6F460,'heapStart':0x801D93A0,'console':'GC','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-P-MQ",'filename':'Legend of Zelda, The - Ocarina of Time - Master Quest (PAL) (GC).dec','actortable':0xB5C480,'scenetable':0xB6F440,'heapStart':0x801D9360,'console':'GC','game':'OoT', 'variation':'MQ'},
    {'name':"OoT-J-GC-CEDisc",'filename':'Zelda no Densetsu - Toki no Ocarina (J) (GC) [Collector\'s Edition Disc].dec','actortable':0xB5CB40,'scenetable':0xB6FB00,'heapStart':0x801DBBA0,'console':'GC','game':'OoT', 'variation':'VANILLA'},
    {'name':"OoT-iQue",'filename':'Zelda Chuanshuo Shiguang Zhi Di 00200f70 (zh-CN) (iQue).dec','actortable':0xB87180,'scenetable':0xB9A120,'heapStart':0x801E7F60,'console':'GC','game':'OoT', 'variation':'VANILLA'},
    {'name':"MM-U",'filename':'Legend of Zelda, The - Majora\'s Mask (USA).dec','actortable':0xC45510,'scenetable':0xC5A1E0,'heapStart':0x803FFDA0,'console':'N64','game':'MM', 'variation': None},
    {'name':"MM-J-1.1",'filename':'Zelda no Densetsu - Mujura no Kamen (Japan) (Rev A).dec','actortable':0xC61AC0,'scenetable':0xC767E0,'heapStart':0x80400230,'console':'N64','game':'MM', 'variation': None},
    ]

actor_names = {
    "OoT": ["Player","_filler_En_Skeleton_filler_","En_Test","_filler_En_Iron_filler_","En_GirlA","_filler_En_Slim_filler_","_filler_En_Bskel_filler_","En_Part","En_Light","En_Door","En_Box","Bg_Dy_Yoseizo","Bg_Hidan_Firewall","En_Poh","En_Okuta","Bg_Ydan_Sp","En_Bom","En_Wallmas","En_Dodongo","En_Firefly","En_Horse","En_Item00","En_Arrow","_filler_Dummy_player_filler_","En_Elf","En_Niw","_filler_En_Bee_filler_","En_Tite","En_Reeba","En_Peehat","En_Butte","_filler_En_F_Obj_filler_","En_Insect","En_Fish","_filler_En_D_Obj_filler_","En_Holl","En_Scene_Change","En_Zf","En_Hata","Boss_Dodongo","Boss_Goma","En_Zl1","En_Viewer","En_Goma","Bg_Pushbox","En_Bubble","Door_Shutter","En_Dodojr","En_Bdfire","_filler_Magic_filler_","En_Boom","En_Torch2","En_Bili","En_Tp","_filler_En_OA1_filler_","En_St","En_Bw","En_A_Obj","En_Eiyer","En_River_Sound","En_Horse_Normal","En_Ossan","Bg_Treemouth","Bg_Dodoago","Bg_Hidan_Dalm","Bg_Hidan_Hrock","En_Horse_Ganon","Bg_Hidan_Rock","Bg_Hidan_Rsekizou","Bg_Hidan_Sekizou","Bg_Hidan_Sima","Bg_Hidan_Syoku","En_Xc","Bg_Hidan_Curtain","Bg_Spot00_Hanebasi","En_Mb","En_Bombf","En_Zl2","Bg_Hidan_Fslift","En_OE2","Bg_Ydan_Hasi","Bg_Ydan_Maruta","Boss_Ganondrof","_filler_En_Npc_filler_","En_Am","En_Dekubaba","En_M_Fire1","En_M_Thunder","Bg_Ddan_Jd","Bg_Breakwall","En_Jj","En_Horse_Zelda","Bg_Ddan_Kd","Door_Warp1","Obj_Syokudai","Item_B_Heart","En_Dekunuts","Bg_Menkuri_Kaiten","Bg_Menkuri_Eye","En_Vali","Bg_Mizu_Movebg","Bg_Mizu_Water","Arms_Hook","En_fHG","Bg_Mori_Hineri","En_Bb","Bg_Toki_Hikari","En_Yukabyun","Bg_Toki_Swd","En_Fhg_Fire","Bg_Mjin","Bg_Hidan_Kousi","Door_Toki","Bg_Hidan_Hamstep","En_Bird","_filler_En_Stree_filler_","_filler_En_Kui_filler_","_filler_En_Maruta_filler_","_filler_En_Saku_filler_","En_Wood02","_filler_En_Twood01_filler_","_filler_En_Kabu02_filler_","_filler_En_Board_filler_","_filler_En_Floater_filler_","En_Lightbox","En_Pu_box","_filler_En_Spia_filler_","_filler_En_Stoneb_filler_","En_Trap","En_Arow_Trap","En_Vase","_filler_Bg_Hidan_Pompfly_filler_","En_Ta","En_Tk","Bg_Mori_Bigst","Bg_Mori_Elevator","Bg_Mori_Kaitenkabe","Bg_Mori_Rakkatenjo","En_Vm","Demo_Effect","Demo_Kankyo","Bg_Hidan_Fwbig","En_Floormas","En_Heishi1","En_Rd","En_Po_Sisters","Bg_Heavy_Block","Bg_Po_Event","Obj_Mure","En_Sw","Boss_Fd","Object_Kankyo","En_Du","En_Fd","En_Horse_Link_Child","Door_Ana","Bg_Spot02_Objects","Bg_Haka","Magic_Wind","Magic_Fire","_filler_Magic_Ice_filler_","En_Ru1","Boss_Fd2","En_Fd_Fire","En_Dh","En_Dha","En_Rl","En_Encount1","Demo_Du","Demo_Im","Demo_Tre_Lgt","En_Fw","Bg_Vb_Sima","En_Vb_Ball","Bg_Haka_Megane","Bg_Haka_MeganeBG","Bg_Haka_Ship","Bg_Haka_Sgami","_filler_Bg_Haka_Kumo_filler_","En_Heishi2","En_Encount2","En_Fire_Rock","En_Brob","Mir_Ray","Bg_Spot09_Obj","Bg_Spot18_Obj","Boss_Va","Bg_Haka_Tubo","Bg_Haka_Trap","Bg_Haka_Huta","Bg_Haka_Zou","Bg_Spot17_Funen","En_Syateki_Itm","En_Syateki_Man","En_Tana","En_Nb","Boss_Mo","En_Sb","En_Bigokuta","En_Karebaba","Bg_Bdan_Objects","Demo_Sa","Demo_Go","En_In","En_Tr","Bg_Spot16_Bombstone","_filler_En_Npc2_filler_","Bg_Hidan_Kowarerukabe","Bg_Bombwall","Bg_Spot08_Iceblock","En_Ru2","Obj_Dekujr","Bg_Mizu_Uzu","Bg_Spot06_Objects","Bg_Ice_Objects","Bg_Haka_Water","_filler_En_Npc3_filler_","En_Ma2","En_Bom_Chu","En_Horse_Game_Check","Boss_Tw","En_Rr","En_Ba","En_Bx","En_Anubice","En_Anubice_Fire","Bg_Mori_Hashigo","Bg_Mori_Hashira4","Bg_Mori_Idomizu","Bg_Spot16_Doughnut","Bg_Bdan_Switch","En_Ma1","Boss_Ganon","Boss_Sst","_filler_Boss_Goma2_filler_","_filler_En_Stk_filler_","En_Ny","En_Fr","Item_Shield","Bg_Ice_Shelter","En_Ice_Hono","Item_Ocarina","_filler_Magic_Light_filler_","_filler_Magic_Soul_filler_","Magic_Dark","Demo_6K","En_Anubice_Tag","Bg_Haka_Gate","Bg_Spot15_Saku","Bg_Jya_Goroiwa","Bg_Jya_Zurerukabe","_filler_Bg_Jya_Sutarukage_filler_","Bg_Jya_Cobra","Bg_Jya_Kanaami","Fishing","Obj_Oshihiki","Bg_Gate_Shutter","Eff_Dust","Bg_Spot01_Fusya","Bg_Spot01_Idohashira","Bg_Spot01_Idomizu","Bg_Po_Syokudai","Bg_Ganon_Otyuka","Bg_Spot15_Rrbox","Bg_Umajump","_filler_Arrow_Dark_filler_","Arrow_Fire","Arrow_Ice","Arrow_Light","_filler_Arrow_Soul_filler_","_filler_Arrow_Wind_filler_","Item_Etcetera","Obj_Kibako","Obj_Tsubo","En_Wonder_Item","En_Ik","Demo_Ik","En_Skj","En_Skjneedle","En_G_Switch","Demo_Ext","Demo_Shd","En_Dns","Elf_Msg","En_Honotrap","En_Tubo_Trap","Obj_Ice_Poly","Bg_Spot03_Taki","Bg_Spot07_Taki","En_Fz","En_Po_Relay","Bg_Relay_Objects","En_Diving_Game","En_Kusa","Obj_Bean","Obj_Bombiwa","_filler_Obj_Breakbox_filler_","_filler_Obj_Hahen_filler_","Obj_Switch","Obj_Elevator","Obj_Lift","Obj_Hsblock","En_Okarina_Tag","En_Yabusame_Mark","En_Goroiwa","En_Ex_Ruppy","En_Toryo","En_Daiku","_filler_En_Stopge_filler_","En_Nwc","En_Blkobj","Item_Inbox","En_Ge1","Obj_Blockstop","En_Sda","En_Clear_Tag","En_Niw_Lady","En_Gm","En_Ms","En_Hs","Bg_Ingate","En_Kanban","En_Heishi3","En_Syateki_Niw","En_Attack_Niw","Bg_Spot01_Idosoko","En_Sa","En_Wonder_Talk","Bg_Gjyo_Bridge","En_Ds","En_Mk","En_Bom_Bowl_Man","En_Bom_Bowl_Pit","En_Owl","En_Ishi","Obj_Hana","Obj_Lightswitch","Obj_Mure2","En_Go","En_Fu","_filler_En_Nc_filler_","En_Changer","Bg_Jya_Megami","Bg_Jya_Lift","Bg_Jya_Bigmirror","Bg_Jya_Bombchuiwa","Bg_Jya_Amishutter","Bg_Jya_Bombiwa","Bg_Spot18_Basket","_filler_En_Warp_Box_filler_","En_Ganon_Organ","En_Siofuki","En_Stream","_filler_En_Zl22_filler_","En_Mm","En_Ko","En_Kz","En_Weather_Tag","Bg_Sst_Floor","En_Ani","En_Ex_Item","Bg_Jya_Ironobj","En_Js","En_Jsjutan","En_Cs","En_Md","En_Hy","En_Ganon_Mant","En_Okarina_Effect","En_Mag","Door_Gerudo","Elf_Msg2","Demo_Gt","En_Po_Field","Efc_Erupc","Bg_Zg","En_Heishi4","En_Zl3","Boss_Ganon2","En_Kakasi","En_Takara_Man","Obj_Makeoshihiki","Oceff_Spot","End_Title","_filler_En_Mother_filler_","En_Torch","Demo_Ec","Shot_Sun","En_Dy_Extra","En_Wonder_Talk2","En_Ge2","Obj_Roomtimer","En_Ssh","En_Sth","Oceff_Wipe","Oceff_Storm","En_Weiyer","Bg_Spot05_Soko","Bg_Jya_1flift","Bg_Jya_Haheniron","Bg_Spot12_Gate","Bg_Spot12_Saku","En_Hintnuts","En_Nutsball","Bg_Spot00_Break","En_Shopnuts","En_It","En_GeldB","Oceff_Wipe2","Oceff_Wipe3","En_Niw_Girl","En_Dog","En_Si","Bg_Spot01_Objects2","Obj_Comb","Bg_Spot11_Bakudankabe","Obj_Kibako2","En_Dnt_Demo","En_Dnt_Jiji","En_Dnt_Nomal","En_Guest","Bg_Bom_Guard","En_Hs2","Demo_Kekkai","Bg_Spot08_Bakudankabe","Bg_Spot17_Bakudankabe","_filler_Bg_Mizu_Switch_filler_","Obj_Mure3","En_Tg","En_Mu","En_Go2","En_Wf","En_Skb","Demo_Gj","Demo_Geff","Bg_Gnd_Firemeiro","Bg_Gnd_Darkmeiro","Bg_Gnd_Soulmeiro","Bg_Gnd_Nisekabe","Bg_Gnd_Iceblock","En_Gb","En_Gs","Bg_Mizu_Bwall","Bg_Mizu_Shutter","En_Daiku_Kakariko","Bg_Bowl_Wall","En_Wall_Tubo","En_Po_Desert","En_Crow","Door_Killer","Bg_Spot11_Oasis","Bg_Spot18_Futa","Bg_Spot18_Shutter","En_Ma3","En_Cow","Bg_Ice_Turara","Bg_Ice_Shutter","En_Kakasi2","En_Kakasi3","Oceff_Wipe4","En_Eg","Bg_Menkuri_Nisekabe","En_Zo","Obj_Makekinsuta","En_Ge3","Obj_Timeblock","Obj_Hamishi","En_Zl4","En_Mm2","Bg_Jya_Block","Obj_Warp2block"],
    "MM": ["Player","En_Test","En_GirlA","En_Part","En_Light","En_Door","En_Box","En_Pametfrog","En_Okuta","En_Bom","En_Wallmas","En_Dodongo","En_Firefly","En_Horse","En_Item00","En_Arrow","En_Elf","En_Niw","En_Tite","_filler_En_Reeba_filler_","En_Peehat","En_Butte","En_Insect","En_Fish","En_Holl","En_Dinofos","En_Hata","En_Zl1","En_Viewer","En_Bubble","Door_Shutter","_filler_En_Dodojr_filler_","En_Boom","En_Torch2","En_Minifrog","_filler_En_Tp_filler_","En_St","_filler_En_Bw_filler_","En_A_Obj","Obj_Wturn","En_River_Sound","_filler_En_Horse_Normal_filler_","En_Ossan","_filler_En_Horse_Ganon_filler_","_filler_En_Xc_filler_","En_Famos","_filler_En_Mb_filler_","En_Bombf","_filler_En_Zl2_filler_","_filler_En_OE2_filler_","En_Am","En_Dekubaba","En_M_Fire1","En_M_Thunder","Bg_Breakwall","_filler_En_Horse_Zelda_filler_","Door_Warp1","Obj_Syokudai","Item_B_Heart","En_Dekunuts","En_Bbfall","Arms_Hook","En_Bb","Bg_Keikoku_Spr","_filler_Bg_Mjin_filler_","En_Wood02","_filler_En_Lightbox_filler_","En_Death","En_Minideath","_filler_En_Ta_filler_","_filler_En_Tk_filler_","En_Vm","Demo_Effect","Demo_Kankyo","En_Floormas","_filler_En_Heishi1_filler_","En_Rd","Bg_F40_Flift","_filler_Bg_Heavy_Block_filler_","Obj_Mure","En_Sw","Object_Kankyo","_filler_En_Du_filler_","_filler_En_Fd_filler_","En_Horse_Link_Child","Door_Ana","_filler_Magic_Wind_filler_","_filler_Magic_Fire_filler_","_filler_En_Fd_Fire_filler_","_filler_En_Dh_filler_","_filler_En_Dha_filler_","En_Encount1","Demo_Tre_Lgt","_filler_En_Fw_filler_","_filler_En_Heishi2_filler_","En_Encount2","En_Fire_Rock","Bg_Ctower_Rot","Mir_Ray","_filler_En_Tana_filler_","En_Sb","En_Bigslime","En_Karebaba","En_In","_filler_En_Tr_filler_","En_Ru","En_Bom_Chu","En_Horse_Game_Check","En_Rr","_filler_En_Ba_filler_","_filler_En_Bx_filler_","_filler_En_Anubice_filler_","_filler_En_Anubice_Fire_filler_","_filler_En_Ma_filler_","_filler_En_Ny_filler_","En_Fr","_filler_Item_Shield_filler_","_filler_En_Ice_Hono_filler_","_filler_Item_Ocarina_filler_","_filler_Magic_Dark_filler_","_filler_En_Anubice_Tag_filler_","_filler_Fishing_filler_","Obj_Oshihiki","Eff_Dust","Bg_Umajump","Arrow_Fire","Arrow_Ice","Arrow_Light","Item_Etcetera","Obj_Kibako","Obj_Tsubo","_filler_En_Wonder_Item_filler_","En_Ik","_filler_En_Skj_filler_","_filler_En_Skjneedle_filler_","_filler_En_G_Switch_filler_","_filler_Demo_Ext_filler_","Demo_Shd","En_Dns","Elf_Msg","En_Honotrap","En_Tubo_Trap","Obj_Ice_Poly","En_Fz","En_Kusa","Obj_Bean","Obj_Bombiwa","Obj_Switch","_filler_Obj_Elevator_filler_","Obj_Lift","Obj_Hsblock","En_Okarina_Tag","_filler_En_Yabusame_Mark_filler_","En_Goroiwa","_filler_En_Ex_Ruppy_filler_","_filler_En_Toryo_filler_","En_Daiku","En_Nwc","Item_Inbox","En_Ge1","Obj_Blockstop","En_Sda","En_Clear_Tag","_filler_En_Niw_Lady_filler_","En_Gm","En_Ms","En_Hs","Bg_Ingate","En_Kanban","_filler_En_Heishi3_filler_","En_Attack_Niw","_filler_En_Sa_filler_","_filler_En_Wonder_Talk_filler_","_filler_En_Ds_filler_","En_Mk","En_Owl","En_Ishi","Obj_Hana","Obj_Lightswitch","Obj_Mure2","_filler_En_Dnc_filler_","En_Fu","_filler_En_Changer_filler_","_filler_En_Siofuki_filler_","En_Stream","En_Mm","_filler_En_Ko_filler_","_filler_En_Kz_filler_","En_Weather_Tag","En_Ani","_filler_En_Ex_Item_filler_","En_Js","_filler_En_Jsjutan_filler_","_filler_En_Cs_filler_","_filler_En_Md_filler_","_filler_En_Hy_filler_","En_Okarina_Effect","En_Mag","Elf_Msg2","Bg_F40_Swlift","_filler_Bg_Zg_filler_","_filler_En_Heishi4_filler_","En_Kakasi","Obj_Makeoshihiki","Oceff_Spot","_filler_End_Title_filler_","En_Torch","_filler_Demo_Ec_filler_","Shot_Sun","_filler_En_Wonder_Talk2_filler_","_filler_En_Ge2_filler_","Obj_Roomtimer","En_Ssh","_filler_En_Sth_filler_","Oceff_Wipe","Oceff_Storm","Obj_Demo","En_Minislime","En_Nutsball","_filler_Bg_Spot00_Break_filler_","_filler_En_Shopnuts_filler_","_filler_En_It_filler_","_filler_En_GeldB_filler_","Oceff_Wipe2","Oceff_Wipe3","_filler_En_Niw_Girl_filler_","En_Dg","En_Si","Obj_Comb","Obj_Kibako2","_filler_En_Guest_filler_","En_Hs2","Obj_Mure3","En_Tg","_filler_En_Mu_filler_","_filler_En_Go2_filler_","En_Wf","En_Skb","_filler_En_Gb_filler_","En_Gs","Obj_Sound","En_Crow","_filler_En_Ma3_filler_","En_Cow","_filler_En_Kakasi2_filler_","_filler_En_Kakasi3_filler_","Oceff_Wipe4","_filler_En_Eg_filler_","En_Zo","Obj_Makekinsuta","En_Ge3","_filler_Obj_Timeblock_filler_","Obj_Hamishi","En_Zl4","En_Mm2","_filler_Obj_Warp2block_filler_","Door_Spiral","_filler_Obj_Fence_filler_","Obj_Pzlblock","Obj_Toge","_filler_Obj_Hampost_filler_","Obj_Armos","Obj_Boyo","_filler_Boss_Dodongo_filler_","_filler_Boss_Goma_filler_","En_Grasshopper","_filler_Obj_Swfl_filler_","Obj_Grass","Obj_Grass_Carry","Obj_Grass_Unit","_filler_En_Gl1_filler_","_filler_En_Gl2_filler_","Bg_Fire_Wall","En_Bu","En_Encount3","En_Jso","Obj_Chikuwa","En_Knight","En_Warp_tag","En_Aob_01","En_Boj_01","En_Boj_02","En_Boj_03","En_Encount4","En_Bom_Bowl_Man","En_Syateki_Man","_filler_En_Takara_Man_filler_","Bg_Icicle","En_Syateki_Crow","En_Boj_04","En_Cne_01","En_Bba_01","En_Bji_01","Bg_Spdweb","_filler_En_Yh_filler_","_filler_En_Mt_filler_","En_Mt_tag","Boss_01","Boss_02","Boss_03","Boss_04","Boss_05","Boss_06","Boss_07","Bg_Dy_Yoseizo","_filler_En_Stay_filler_","En_Boj_05","_filler_En_Of1_01_filler_","_filler_En_Gskb_filler_","En_Sob1","_filler_En_Of1_02_filler_","_filler_En_Of1_03_filler_","En_Go","_filler_En_Of1_05_filler_","En_Raf","Obj_Funen","Obj_Raillift","Bg_Numa_Hana","Obj_Flowerpot","Obj_Spinyroll","Dm_Hina","En_Syateki_Wf","Obj_Skateblock","Obj_Iceblock","En_Bigpamet","En_Syateki_Dekunuts","Elf_Msg3","En_Fg","Dm_Ravine","Dm_Sa","En_Slime","En_Pr","Obj_Toudai","Obj_Entotu","Obj_Bell","En_Syateki_Okuta","_filler_En_Colociam_filler_","Obj_Shutter","Dm_Zl","En_Elfgrp","Dm_Tsg","En_Baguo","Obj_Vspinyroll","Obj_Smork","En_Test2","En_Test3","En_Test4","En_Bat","En_Sekihi","En_Wiz","En_Wiz_Brock","En_Wiz_Fire","Eff_Change","Dm_Statue","Obj_Fireshield","Bg_Ladder","En_Mkk","Demo_Getitem","_filler_Obj_Stain_filler_","En_Dnb","En_Dnh","En_Dnk","En_Dnq","_filler_En_Dnc_Tag_filler_","Bg_Keikoku_Saku","Obj_Hugebombiwa","En_Firefly2","En_Rat","En_Water_Effect","En_Kusa2","Bg_Spout_Fire","_filler_En_TimeTime_filler_","Bg_Dblue_Movebg","En_Dy_Extra","En_Bal","En_Ginko_Man","En_Warp_Uzu","Obj_Driftice","En_Look_Nuts","En_Mushi2","En_Fall","En_Mm3","Bg_Crace_Movebg","En_Dno","En_Pr2","En_Prz","En_Jso2","Obj_Etcetera","En_Egol","Obj_Mine","Obj_Purify","En_Tru","En_Trt","_filler_En_Egrock_filler_","_filler_En_Sd_filler_","En_Test5","En_Test6","En_Az","En_Estone","Bg_Hakugin_Post","Dm_Opstage","Dm_Stk","Dm_Char00","Dm_Char01","Dm_Char02","Dm_Char03","Dm_Char04","Dm_Char05","Dm_Char06","Dm_Char07","Dm_Char08","Dm_Char09","Obj_Tokeidai","_filler_En_Goron_game_check_filler_","En_Mnk","En_Egblock","En_Guard_Nuts","Bg_Hakugin_Bombwall","Obj_Tokei_Tobira","Bg_Hakugin_Elvpole","En_Ma4","En_Twig","En_Po_Fusen","En_Door_Etc","En_Bigokuta","Bg_Icefloe","Obj_Ocarinalift","En_Time_Tag","Bg_Open_Shutter","Bg_Open_Spot","Bg_Fu_Kaiten","Obj_Aqua","En_Elforg","En_Elfbub","_filler_En_Ton_filler_","En_Fu_Mato","En_Fu_Kago","En_Osn","Bg_Ctower_Gear","En_Trt2","Obj_Tokei_Step","Bg_Lotus","En_Kame","Obj_Takaraya_Wall","Bg_Fu_Mizu","En_Sellnuts","Bg_Dkjail_Ivy","_filler_En_Ton2_filler_","Obj_Visiblock","En_Takaraya","En_Tsn","En_Ds2n","En_Fsn","En_Shn","_filler_En_Ton_bal_filler_","En_Stop_heishi","Obj_Bigicicle","En_Lift_Nuts","En_Tk","_filler_En_Ton3_filler_","Bg_Market_Step","Obj_Lupygamelift","En_Test7","Obj_Lightblock","Mir_Ray2","En_Wdhand","En_Gamelupy","Bg_Danpei_Movebg","En_Snowwd","En_Pm","En_Gakufu","Elf_Msg4","Elf_Msg5","En_Col_Man","En_Talk_Gibud","En_Giant","Obj_Snowball","Boss_Hakugin","En_Gb2","En_Onpuman","Bg_Tobira01","En_Tag_Obj","Obj_Dhouse","Obj_Hakaisi","Bg_Hakugin_Switch","_filler_En_Btlpoh_filler_","En_Snowman","TG_Sw","En_Po_Sisters","En_Pp","En_Hakurock","En_Hanabi","Obj_Dowsing","Obj_Wind","En_Racedog","En_Kendo_Js","Bg_Botihasira","En_Fish2","En_Pst","En_Poh","Obj_Spidertent","En_Zoraegg","En_Kbt","En_Gg","En_Maruta","Obj_Snowball2","En_Gg2","Obj_Ghaka","En_Dnp","En_Dai","Bg_Goron_Oyu","En_Kgy","En_Invadepoh","En_Gk","En_An","_filler_En_Sellnuts2_filler_","En_Bee","En_Ot","En_Dragon","Obj_Dora","En_Bigpo","Obj_Kendo_Kanban","Obj_Hariko","En_Sth","Bg_Sinkai_Kabe","Bg_Haka_Curtain","Bg_Kin2_Bombwall","Bg_Kin2_Fence","Bg_Kin2_Picture","Bg_Kin2_Shelf","En_Rail_Skb","En_Jg","En_Tru_Mt","Obj_Um","En_Neo_Reeba","Bg_Mbar_Chair","Bg_Ikana_Block","Bg_Ikana_Mirror","Bg_Ikana_Rotaryroom","Bg_Dblue_Balance","Bg_Dblue_Waterfall","En_Kaizoku","En_Ge2","En_Ma_Yts","En_Ma_Yto","Obj_Tokei_Turret","Bg_Dblue_Elevator","Obj_Warpstone","En_Zog","Obj_Rotlift","Obj_Jg_Gakki","Bg_Inibs_Movebg","En_Zot","Obj_Tree","Obj_Y2lift","Obj_Y2shutter","Obj_Boat","Obj_Taru","Obj_Hunsui","En_Jc_Mato","Mir_Ray3","En_Zob","Elf_Msg6","Obj_Nozoki","En_Toto","En_Railgibud","En_Baba","En_Suttari","En_Zod","En_Kujiya","En_Geg","Obj_Kinoko","Obj_Yasi","En_Tanron1","En_Tanron2","En_Tanron3","Obj_Chan","En_Zos","En_S_Goro","En_Nb","En_Ja","Bg_F40_Block","Bg_F40_Switch","En_Po_Composer","En_Guruguru","Oceff_Wipe5","En_Stone_heishi","Oceff_Wipe6","En_Scopenuts","En_Scopecrow","Oceff_Wipe7","Eff_Kamejima_Wave","En_Hg","En_Hgo","En_Zov","En_Ah","Obj_Hgdoor","Bg_Ikana_Bombwall","Bg_Ikana_Ray","Bg_Ikana_Shutter","Bg_Haka_Bombwall","Bg_Haka_Tomb","En_Sc_Ruppe","Bg_Iknv_Doukutu","Bg_Iknv_Obj","En_Pamera","Obj_HsStump","En_Hidden_Nuts","En_Zow","En_Talk","En_Al","En_Tab","En_Nimotsu","En_Hit_Tag","En_Ruppecrow","En_Tanron4","En_Tanron5","En_Tanron6","En_Daiku2","En_Muto","En_Baisen","En_Heishi","En_Demo_heishi","En_Dt","En_Cha","Obj_Dinner","Eff_Lastday","Bg_Ikana_Dharma","En_Akindonuts","Eff_Stk","En_Ig","En_Rg","En_Osk","En_Sth2","En_Yb","En_Rz","En_Scopecoin","En_Bjt","En_Bomjima","En_Bomjimb","En_Bombers","En_Bombers2","En_Bombal","Obj_Moon_Stone","Obj_Mu_Pict","Bg_Ikninside","Eff_Zoraband","Obj_Kepn_Koya","Obj_Usiyane","En_Nnh","Obj_Kzsaku","Obj_Milk_Bin","En_Kitan","Bg_Astr_Bombwall","Bg_Iknin_Susceil","En_Bsb","En_Recepgirl","En_Thiefbird","En_Jgame_Tsn","Obj_Jgame_Light","Obj_Yado","Demo_Syoten","Demo_Moonend","Bg_Lbfshot","Bg_Last_Bwall","En_And","En_Invadepoh_Demo","Obj_Danpeilift","En_Fall2","Dm_Al","Dm_An","Dm_Ah","Dm_Nb","En_Drs","En_Ending_Hero","Dm_Bal","En_Paper","En_Hint_Skb","Dm_Tag","En_Bh","En_Ending_Hero2","En_Ending_Hero3","En_Ending_Hero4","En_Ending_Hero5","En_Ending_Hero6","Dm_Gm","Obj_Swprize","En_Invisible_Ruppe","Obj_Ending","En_Rsn"],
    "AF": ["Player","BgItem","Sample","Fieldm_Draw","Field_Draw","Airplane","Room_Sunshine","Lamp_Light","Ev_Angler","Ball","Haniwa","My_Room","Mbg","T_Tama","BoxManager","BoxMove","BoxTrick01","Arrange_Room","Arrange_Furniture","TrainDoor","T_Keitai","Halloween_Npc","Ev_Pumpkin","Ride_Off_Demo","Npc_Mamedanuki","Hanabi_Npc0","Hanabi_Npc1","Snowman","Npc_Post_Girl","Npc_Engineer","Npc_Majin3","Npc_Sleep_Obaba","Npc","Effect_Control","Npc2","Kamakura_Npc0","Npc_Post_Man","Shop_Design","Quest_Manager","MailBox","House","Shop_Level","Shop","MyHouse","Ev_Artist","Ev_Broker","Ev_Designer","T_Umbrella","Npc_Shop_Master","Birth_Control","Shop_Manekin","Shop_Indoor","Event_Manager","Shop_Goods","BrShop","Weather","Post_Office","Npc_Guide","Npc_Guide2","Insect","Station","Ev_CarpetPeddler","Ev_KabuPeddler","Reserve","HandOverItem","Npc_Conv_Master","Npc_Super_Master","Npc_Depart_Master","Tools","Structure","Ev_Gypsy","Npc_Police","Train0","Train1","Npc_Station_Master","Ev_Santa","Npc_Police2","Police_Box","BgPoliceItem","BgCherryItem","BgWinterItem","BgXmasItem","BgPostItem","FallS","FallSESW","Ev_Broker2","Broker_Design","T_Utiwa","Psnowman","My_Indoor","Npc_Rcn_Guide","Intro_Demo","Shrine","Buggy","T_Hanabi","Conveni","Super","Depart","Hanami_Npc0","S_Car","Hanami_Npc1","Npc_P_Sel","Npc_P_Sel2","Npc_Rcn_Guide2","Train_Window","Npc_Majin4","Kamakura","Gyoei","Npc_Majin","T_NpcSao","_filler_Train_Control_filler_","Uki","Npc_Majin2","Normal_Npc","Set_Manager","Set_Npc_Manager","Npc_Shop_Mastersp","Room_Sunshine_Posthouse","Room_Sunshine_Police","Effectbg","Ev_Cherry_Manager","Ev_Yomise","Tokyoso_Npc0","Tokyoso_Npc1","Goza","Radio","Yatai","Tokyoso_Control","Shop_Umbrella","Gyo_Release","Tukimi","Kamakura_Indoor","Ev_Miko","Gyo_Kage","Mikuji","House_Goki","T_Cracker","_filler_T_Sensu_filler_","T_Pistol","T_Flag","T_Tumbler","Tukimi_Npc0","Tukimi_Npc1","_filler_Tukimi_Npc2_filler_","Countdown_Npc0","Countdown_Npc1","Turi_Npc0","Taisou_Npc0","Count","Garagara","Tamaire_Npc0","Tamaire_Npc1","Hatumode_Npc0","Npc_Totakeke","Count02","Hatumode_Control","Tama","Kago","Turi","House_Clock","Tunahiki_Control","Tunahiki_Npc0","Tunahiki_Npc1","Koinobori","Bee","Nameplate","Dump","Rope","Ev_Dozaemon","Windmill","Lotus","Animal_Logo","Mikanbox","Douzou","Npc_Rtc","Toudai","Npc_Restart","Npc_Majin5","Fuusen","Ev_Dokutu","Dummy","_filler_Dummy2C_filler_","_filler_Dummy2D_filler_","_filler_Dummy2E_filler_","_filler_Dummy2F_filler_","_filler_Dummy30_filler_","_filler_Dummy31_filler_","_filler_Dummy32_filler_","_filler_Dummy33_filler_","_filler_Dummy34_filler_","_filler_Dummy35_filler_","_filler_Dummy36_filler_","_filler_Dummy37_filler_","_filler_Dummy38_filler_","_filler_Dummy39_filler_","_filler_Dummy3A_filler_","_filler_Dummy3B_filler_","_filler_Dummy3C_filler_","_filler_Dummy3D_filler_","_filler_Dummy3E_filler_","_filler_Dummy3F_filler_"]
}

versionDict = {}
for v in versions:
    versionDict[v['name']] = v
f2 = open('versions.json','w')
json.dump(versionDict,f2,indent='\t')
f2.close()

###########################################

actor_count = {
    "OoT": 0x1D7,
    "MM": 0x02B2
}

hardcoded_init_vars = {
    "OoT": {
        0x0: b'\x00\x00\x02\x00\x06\x00\x00\x35\x00\x01\x00\x00\x00\x00\x0A\x84\x80\x09\x7D\xA8\x80\x09\x7D\xF0\x80\x09\x7E\x30\x80\x09\x7E\x70', # Player
        0x15: b'\x00\x15\x08\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x9C\x80\x01\x21\x8C\x80\x01\x27\xF4\x80\x01\x2F\x78\x80\x01\x35\xF8', # En_Item00
        0x39: b'\x00\x39\x06\x00\x00\x00\x00\x10\x00\x01\x00\x00\x00\x00\x01\xB8\x80\x01\x16\xEC\x80\x01\x1A\x2C\x80\x01\x1F\x74\x80\x01\x20\x90' # En_A_Obj
    },
    "MM": {
        0x0: b'\x00\x00\x02\x00\x86\x20\x00\x39\x00\x01\x00\x00\x00\x00\x0D\x78\x80\x16\x0A\xF8\x80\x16\x0B\x40\x80\x16\x0B\x80\x80\x16\x0B\xC0', # Player
        0xE: b'\x00\x0E\x08\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\xA8\x80\x0A\x5D\x70\x80\x0A\x63\x7C\x80\x0A\x6B\x98\x80\x0A\x71\x28', # En_Item00
        0x26: b'\x00\x26\x06\x00\x00\x00\x00\x09\x00\x01\x00\x00\x00\x00\x01\x94\x80\x0A\x5A\xC0\x80\x0A\x5B\x6C\x80\x0A\x5C\x60\x80\x0A\x5C\xB8' # En_A_Obj
    }
}

actors = {
    "OoT": [{} for _ in range(actor_count["OoT"])],
    "MM": [{} for _ in range(actor_count["MM"])]
}

for v in versions:
    print(v['name'])
    f=open('roms/'+v['filename'],'rb')
    rom = f.read()

    for actorId in range(actor_count[v['game']]):
        romStart, romEnd, ramStart, ramEnd, _, ramInitVars, _, allocType, _, _ = struct.unpack('>IIIIIIIhbb',rom[v['actortable']+0x20*actorId:v['actortable']+0x20*(actorId+1)])
        overlaySize = ramEnd-ramStart
        romInitVars = romStart+ramInitVars-ramStart
        if 0 < romInitVars < 0x80000000:
            initVars = rom[romInitVars:romInitVars+0x20]
        elif ramInitVars > 0:
            initVars = hardcoded_init_vars[v['game']][actorId]
        else:
            initVars = None
            
        if initVars:
            _,actorType,_,_,objectId,_,instanceSize,_,_,_,drawPtr = struct.unpack('>HBBIHHIIIII',initVars)
            actorInfo = {'actorId':actorId,'actorType':actorType,'overlaySize':overlaySize, 'instanceSize':instanceSize, 'allocType':allocType, 'name':actor_names[v['game']][actorId], 'objectId':objectId,'drawPtr':drawPtr}
        else:
            actorInfo = {'name':actor_names[v['game']][actorId]}
        actors[v['game']][actorId][v['name']] = actorInfo

#for i in range(actor_count):
#    if (actors[i]["N-1.0"]==actors[i]["N-1.1"]==actors[i]["P-1.0"]==actors[i]["N-1.2"]==actors[i]["P-1.1"]==
#        actors[i]["J-GC-MQDisc"]==actors[i]["J-MQ"]==actors[i]["U-GC"]==actors[i]["U-MQ"]==actors[i]["P-GC"]==actors[i]["P-MQ"]==actors[i]["J-GC-CEDisc"]):
#        actors[i] = {'ALL':actors[i]["N-1.0"]}
#    elif (actors[i]["N-1.0"]==actors[i]["N-1.1"]==actors[i]["P-1.0"]==actors[i]["N-1.2"]==actors[i]["P-1.1"]) and (
#        actors[i]["J-GC-MQDisc"]==actors[i]["J-MQ"]==actors[i]["U-GC"]==actors[i]["U-MQ"]==actors[i]["P-GC"]==actors[i]["P-MQ"]==actors[i]["J-GC-CEDisc"]):
#        actors[i] = {'N64':actors[i]["N-1.0"],'GC':actors[i]["J-GC-MQDisc"]}
#    else:
#        pass

f2 = open('actors.json','w')
json.dump(actors,f2,indent='\t')
f2.close()

for v in actors['OoT'][0]:
    f2 = open('csv/actors_%s.csv'%v,'w')
    f2.write('Actor ID,Actor Name,Instance Size (without header),Overlay Size (without header),Instance Size (with header),Overlay Size (with header),Allocation Type,Object ID\n')
    for i in range(len(actors['OoT'])):
        if 'instanceSize' in actors['OoT'][i][v]:
            instanceSize = actors['OoT'][i][v]['instanceSize']
            overlaySize = actors['OoT'][i][v]['overlaySize']
            while instanceSize % 0x10 > 0:
                instanceSize += 1
            while overlaySize % 0x10 > 0:
                overlaySize += 1
            headerSize = {'GC':0x10,'N64':0x30}[versionDict[v]['console']]
            if overlaySize != 0:
                f2.write("0x%04X,%s,0x%X,0x%X,0x%X,0x%X,%d,0x%04X\n"%(i,actors['OoT'][i][v]['name'],instanceSize,overlaySize,instanceSize+headerSize,overlaySize+headerSize,actors['OoT'][i][v]['allocType'],actors['OoT'][i][v]['objectId']))
            else:
                f2.write("0x%04X,%s,0x%X,,0x%X,,%d,0x%04X\n"%(i,actors['OoT'][i][v]['name'],instanceSize,instanceSize+headerSize,actors['OoT'][i][v]['allocType'],actors['OoT'][i][v]['objectId']))
        else:
            f2.write("0x%04X,%s,,,,,\n"%(i,actors['OoT'][i][v]['name']))
    f2.close()

#########################################################

scene_count = {
    "OoT": 0x65,
    "MM": 0x71
}

scenes = {
    "OoT": [{} for _ in range(scene_count["OoT"])],
    "MM": [{} for _ in range(scene_count["MM"])]
}

min_setup_count = {
    "OoT": 4,
    "MM": 1
}

for v in versions:
    print(v['name'])
    f=open('roms/'+v['filename'],'rb')
    rom = f.read()

    for sceneId in range(scene_count[v['game']]):

        scenes[v['game']][sceneId][v['name']] = [None] * min_setup_count[v['game']]

        if v['game'] == 'MM':
            sceneRomStart, sceneRomEnd, _, _ = struct.unpack('>IIII',rom[v['scenetable']+0x10*sceneId:v['scenetable']+0x10*(sceneId+1)])
        else:
            sceneRomStart, sceneRomEnd, _, _, _ = struct.unpack('>IIIII',rom[v['scenetable']+0x14*sceneId:v['scenetable']+0x14*(sceneId+1)])
        #print('scene', hex(sceneId), hex(sceneRomStart), hex(sceneRomEnd))

        if sceneRomStart==0 and sceneRomEnd==0:
            continue # null entry

        sceneAltHeaders = None
        roomAltHeaders = {}

        for setupId in range(min_setup_count[v['game']]):

            #print('setup', hex(setupId))
            if setupId == 0:
                scenes[v['game']][sceneId][v['name']][setupId] = {'rooms':[],'transitionActors':[],'specialObject':0}
                sceneHeaderStart = sceneRomStart
            else:
                if sceneAltHeaders and sceneAltHeaders[setupId-1]:
                    scenes[v['game']][sceneId][v['name']][setupId] = {'rooms':[],'transitionActors':[],'specialObject':0}
                    sceneHeaderStart = sceneRomStart + (sceneAltHeaders[setupId-1]&0x00FFFFFF)
                else:
                    scenes[v['game']][sceneId][v['name']][setupId] = None
                    continue
            
            sceneHeaderCommand = None
            sceneHeaderNum = 0
            while sceneHeaderCommand != 0x14:
                sceneHeaderCommand, sceneParam1, _, sceneParam2 = struct.unpack('>BBHI',rom[sceneHeaderStart+8*sceneHeaderNum:sceneHeaderStart+8*(sceneHeaderNum+1)])

                #print('cmd',hex(sceneHeaderCommand))
                assert sceneHeaderCommand < 0x1F
                if sceneHeaderCommand == 0x18: # Alternate Headers
                    sceneSetupListStart = sceneRomStart + (sceneParam2&0x00FFFFFF)
                    sceneAltHeaders = struct.unpack('>III', rom[sceneSetupListStart:sceneSetupListStart+0xC]) # we only care about setups 0-3
                elif sceneHeaderCommand == 0x04: # Rooms
                    for roomId in range(sceneParam1):
                        roomListStart = sceneRomStart + (sceneParam2&0x00FFFFFF)
                        roomRomStart, roomRomEnd = struct.unpack('>II',rom[roomListStart+8*roomId:roomListStart+8*(roomId+1)])

                        roomData = {'actors':[],'objects':[]}

                        if setupId == 0:
                            roomHeaderStart = roomRomStart
                        else:
                            assert(roomAltHeaders[roomId][setupId-1])
                            roomHeaderStart = roomRomStart + (roomAltHeaders[roomId][setupId-1]&0x00FFFFFF)
                        
                        roomHeaderCommand = None
                        roomHeaderNum = 0
                        while roomHeaderCommand != 0x14:
                            roomHeaderCommand, roomParam1, _, roomParam2 = struct.unpack('>BBHI',rom[roomHeaderStart+8*roomHeaderNum:roomHeaderStart+8*(roomHeaderNum+1)])

                            if roomHeaderCommand == 0x18: # Alternate Headers
                                roomSetupListStart = roomRomStart + (roomParam2&0x00FFFFFF)
                                roomAltHeaders[roomId] = struct.unpack('>III', rom[roomSetupListStart:roomSetupListStart+0xC]) # we only care about setups 0-3
                            elif roomHeaderCommand == 0x0B: #Object List
                                for objectNum in range(roomParam1):
                                    objectListStart = roomRomStart + (roomParam2&0x00FFFFFF)
                                    obj = struct.unpack('>H',rom[objectListStart+0x2*objectNum:objectListStart+0x2*(objectNum+1)])[0]
                                    roomData['objects'].append(obj)
                            elif roomHeaderCommand == 0x01: #Actor List
                                for actorNum in range(roomParam1):
                                    actorListStart = roomRomStart + (roomParam2&0x00FFFFFF)
                                    if v['game'] == 'MM':
                                        actorId, posX, posY, posZ, spawnTimeHi, _, spawnTimeLo, actorParams = struct.unpack('>HhhhHHHH',rom[actorListStart+0x10*actorNum:actorListStart+0x10*(actorNum+1)])
                                        actorId &= 0xFFF
                                        spawnTimeBits = ((spawnTimeHi & 0x7) << 7) | spawnTimeLo & 0x7F
                                        spawnTime = [(spawnTimeBits>>x) & 1 for x in reversed(range(10))]
                                        roomData['actors'].append({'actorId':actorId,'actorParams':actorParams,'position':(posX,posY,posZ),'spawnTime':spawnTime})
                                    else:
                                        actorId, posX, posY, posZ, _, _, _, actorParams = struct.unpack('>HhhhHHHH',rom[actorListStart+0x10*actorNum:actorListStart+0x10*(actorNum+1)])
                                        roomData['actors'].append({'actorId':actorId,'actorParams':actorParams,'position':(posX,posY,posZ)})
                            roomHeaderNum += 1
                            
                        scenes[v['game']][sceneId][v['name']][setupId]['rooms'].append(roomData)
            
                elif sceneHeaderCommand == 0x0E: # Transition Actors
                    for transitionActorNum in range(sceneParam1):
                        transitionActorListStart = sceneRomStart + (sceneParam2&0x00FFFFFF)
                        frontRoom, _, backRoom, _, actorId, _, _, _, _, actorParams = struct.unpack('>BBBBHHHHHH',rom[transitionActorListStart+0x10*transitionActorNum:transitionActorListStart+0x10*(transitionActorNum+1)])
                        scenes[v['game']][sceneId][v['name']][setupId]['transitionActors'].append({'frontRoom':frontRoom,'backRoom':backRoom,'actorId':actorId,'actorParams':actorParams})

                elif sceneHeaderCommand == 0x07: # Special Objects
                    assert sceneParam2 in [0,2,3]
                    scenes[v['game']][sceneId][v['name']][setupId]['specialObject'] = sceneParam2
                
                sceneHeaderNum += 1
                
            if sceneAltHeaders:
                assert len(roomAltHeaders) == len(scenes[v['game']][sceneId][v['name']][setupId]['rooms'])
            else:
                assert len(roomAltHeaders) == 0
            
#for i in range(scene_count):
#    if (scenes[i]["N-1.0"]==scenes[i]["N-1.1"]==scenes[i]["P-1.0"]==scenes[i]["N-1.2"]==scenes[i]["P-1.1"]==scenes[i]["J-GC-MQDisc"]==scenes[i]["U-GC"]==scenes[i]["P-GC"]==scenes[i]["J-GC-CEDisc"]
#        ==scenes[i]["J-MQ"]==scenes[i]["U-MQ"]==scenes[i]["P-MQ"]):
#        scenes[i] = {'ALL':scenes[i]["N-1.0"]}
#    elif (scenes[i]["N-1.0"]==scenes[i]["N-1.1"]==scenes[i]["P-1.0"]==scenes[i]["N-1.2"]==scenes[i]["P-1.1"]==scenes[i]["J-GC-MQDisc"]==scenes[i]["U-GC"]==scenes[i]["P-GC"]==scenes[i]["J-GC-CEDisc"]
#          ) and (scenes[i]["J-MQ"]==scenes[i]["U-MQ"]==scenes[i]["P-MQ"]):
#        scenes[i] = {'VANILLA':scenes[i]["N-1.0"],'MQ':scenes[i]["J-MQ"]}
#    else:
#        pass

f2 = open('scenes.json','w')
json.dump(scenes,f2,indent='\t')
f2.close()
