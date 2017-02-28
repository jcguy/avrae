'''
Created on Jan 13, 2017

@author: andrew
'''
import json
from math import floor
import math

from utils.functions import print_table, discord_trim, fuzzy_search


def searchCondition(condition):
    with open('./res/conditions.json', 'r') as f:
        conditions = json.load(f)
    return fuzzy_search(conditions, 'name', condition)

def searchMonster(monstername, visible=True, return_monster=False):
    with open('./res/bestiary.json', 'r') as f:
        monsters = json.load(f)
    
    monsterDesc = []

    try:
        monster = next(item for item in monsters if monstername.upper() == item["name"].upper())
    except Exception:
        try:
            monster = next(item for item in monsters if monstername.upper() in item["name"].upper())
        except Exception:
            monsterDesc.append("Monster does not exist or is misspelled.")
            if return_monster: return {'monster': None, 'string': monsterDesc}
            return monsterDesc
        
    def parsesource (src):
        source = src
        if (source == " monster manual"): source = "MM";
        if (source == " Volo's Guide"): source = "VGM";
        if (source == " elemental evil"): source = "PotA";
        if (source == " storm kings thunder"): source = "SKT";
        if (source == " tyranny of dragons"): source = "ToD";
        if (source == " out of the abyss"): source = "OotA";
        if (source == " curse of strahd"): source = "CoS";
        if (source == " lost mine of phandelver"): source = "LMoP";
        if (source == " tome of beasts"): source = "ToB 3pp";
        return source;
    
    def parsesourcename (src):
        source = src;
        if (source == " monster manual"): source = "Monster Manual";
        if (source == " Volo's Guide"): source = "Volo's Guide to Monsters";
        if (source == " elemental evil"): source = "Princes of the Apocalypse";
        if (source == " storm kings thunder"): source = "Storm King's Thunder";
        if (source == " tyranny of dragons"): source = "Tyranny of Dragons";
        if (source == " out of the abyss"): source = "Out of the Abyss";
        if (source == " curse of strahd"): source = "Curse of Strahd";
        if (source == " lost mine of phandelver"): source = "Lost Mine of Phandelver";
        if (source == " tome of beasts"): source = "Tome of Beasts (3pp)";
        return source;
    
    def parsesize (size):
        if (size == "T"): size = "Tiny";
        if (size == "S"): size = "Small";
        if (size == "M"): size = "Medium";
        if (size == "L"): size = "Large";
        if (size == "H"): size = "Huge";
        if (size == "G"): size = "Gargantuan";
        return size;
    
    if visible:
            
        monster['size'] = parsesize(monster['size'])
        monster['type'] = ','.join(monster['type'].split(',')[:-1])
        for stat in ['str', 'dex', 'con', 'wis', 'int', 'cha']:
            monster[stat + 'Str'] = monster[stat] + " ({:+})".format(floor((int(monster[stat])-10)/2))
        if monster.get('skill') is not None:
            monster['skill'] = monster['skill'][0]
        if monster.get('senses') is None:
            monster['senses'] = "passive Perception {}".format(monster['passive'])
        else:
            monster['senses'] = monster.get('senses') + ", passive Perception {}".format(monster['passive'])
        
        monsterDesc.append("{name}, {size} {type}. {alignment}.\n**AC:** {ac}.\n**HP:** {hp}.\n**Speed:** {speed}\n".format(**monster))
        monsterDesc.append("**STR:** {strStr} **DEX:** {dexStr} **CON:** {conStr} **WIS:** {wisStr} **INT:** {intStr} **CHA:** {chaStr}\n".format(**monster))
        if monster.get('save') is not None:
            monsterDesc.append("**Saving Throws:** {save}\n".format(**monster))
        if monster.get('skill') is not None:
            monsterDesc.append("**Skills:** {skill}\n".format(**monster))
        monsterDesc.append("**Senses:** {senses}.\n".format(**monster))
        if monster.get('vulnerable', '') is not '':
            monsterDesc.append("**Vulnerabilities:** {vulnerable}\n".format(**monster))
        if monster.get('resist', '') is not '':
            monsterDesc.append("**Resistances:** {resist}\n".format(**monster))
        if monster.get('immune', '') is not '':
            monsterDesc.append("**Damage Immunities:** {immune}\n".format(**monster))
        if monster.get('conditionImmune', '') is not '':
            monsterDesc.append("**Condition Immunities:** {conditionImmune}\n".format(**monster))
        if monster.get('languages', '') is not '':
            monsterDesc.append("**Languages:** {languages}\n".format(**monster))
        else:
            monsterDesc.append("**Languages:** --\n".format(**monster))
        monsterDesc.append("**CR:** {cr}\n".format(**monster))
        
        attacks = [] # setup things
        if "trait" in monster:
            monsterDesc.append("\n**__Special Abilities:__**\n")
            for a in monster["trait"]:
                if isinstance(a['text'], list):
                    a['text'] = '\n'.join(t for t in a['text'] if t is not None)
                monsterDesc.append("**{name}:** {text}\n".format(**a))
                if 'attack' in a:
                    attacks.append(a)
        if "action" in monster:
            monsterDesc.append("\n**__Actions:__**\n")
            for a in monster["action"]:      
                if isinstance(a['text'], list):
                    a['text'] = '\n'.join(t for t in a['text'] if t is not None)
                monsterDesc.append("**{name}:** {text}\n".format(**a))
                if 'attack' in a:
                    attacks.append(a)
            
        if "reaction" in monster:
            monsterDesc.append("\n**__Reactions:__**\n")
            monsterDesc.append("**{name}:** {text}\n".format(**monster['reaction']))
            if 'attack' in a:
                attacks.append(a)
            
        if "legendary" in monster:
            monsterDesc.append("\n**__Legendary Actions:__**\n")
            for a in monster["legendary"]:
                if isinstance(a['text'], list):
                    a['text'] = '\n'.join(t for t in a['text'] if t is not None)
                if a['name'] is not '':
                    monsterDesc.append("**{name}:** {text}\n".format(**a))
                else:
                    monsterDesc.append("{text}\n".format(**a))
                if 'attack' in a:
                    attacks.append(a)
                    
        # fix list of attack dicts
        tempAttacks = []
        for a in attacks:
            desc = a['text']
            parentName = a['name']
            for atk in a['attack']:
                if atk is None: continue
                data = atk.split('|')
                name = data[0] if not data[0] == '' else parentName
                toHit = data[1] if not data[1] == '' else None
                damage = data[2] if not data[2] == '' else None
                atkObj = {'name': name,
                          'desc': desc,
                          'attackBonus': toHit,
                          'damage': damage}
                tempAttacks.append(atkObj)
        monster['attacks'] = tempAttacks
    else:
        monster['hp'] = int(monster['hp'].split(' (')[0])
        monster['ac'] = int(monster['ac'].split(' (')[0])
        monster['size'] = parsesize(monster['size'])
        monster['type'] = ','.join(monster['type'].split(',')[:-1])
        if monster["hp"] < 10:
            monster["hp"] = "Very Low"
        elif 10 <= monster["hp"] < 50:
            monster["hp"] = "Low"
        elif 50 <= monster["hp"] < 100:
            monster["hp"] = "Medium"
        elif 100 <= monster["hp"] < 200:
            monster["hp"] = "High"
        elif 200 <= monster["hp"] < 400:
            monster["hp"] = "Very High"
        elif 400 <= monster["hp"]:
            monster["hp"] = "Godly"
            
        if monster["ac"] < 6:
            monster["ac"] = "Very Low"
        elif 6 <= monster["ac"] < 9:
            monster["ac"] = "Low"
        elif 9 <= monster["ac"] < 15:
            monster["ac"] = "Medium"
        elif 15 <= monster["ac"] < 17:
            monster["ac"] = "High"
        elif 17 <= monster["ac"] < 22:
            monster["ac"] = "Very High"
        elif 22 <= monster["ac"]:
            monster["ac"] = "Godly"
            
        for stat in ["str", "dex", "con", "wis", "int", "cha"]:
            monster[stat] = int(monster[stat])
            if monster[stat] <= 3:
                monster[stat] = "Very Low"
            elif 3 < monster[stat] <= 7:
                monster[stat] = "Low"
            elif 7 < monster[stat] <= 15:
                monster[stat] = "Medium"
            elif 15 < monster[stat] <= 21:
                monster[stat] = "High"
            elif 21 < monster[stat] <= 25:
                monster[stat] = "Very High"
            elif 25 < monster[stat]:
                monster[stat] = "Godly"
                
        if monster.get("languages"):
            monster["languages"] = len(monster["languages"].split(", "))
        else:
            monster["languages"] = 0
        
        monsterDesc.append("{name}, {size} {type}.\n" \
        "**AC:** {ac}.\n**HP:** {hp}.\n**Speed:** {speed}\n" \
        "**STR:** {str} **DEX:** {dex} **CON:** {con} **WIS:** {wis} **INT:** {int} **CHA:** {cha}\n" \
        "**Languages:** {languages}\n".format(**monster))
        
        if "trait" in monster:
            monsterDesc.append("**__Special Abilities:__** " + str(len(monster["trait"])) + "\n")
        
        monsterDesc.append("**__Actions:__** " + str(len(monster["action"])) + "\n")
        
        if "reaction" in monster:
            monsterDesc.append("**__Reactions:__** " + str(len(monster["reaction"])) + "\n")
            
        if "legendary" in monster:
            monsterDesc.append("**__Legendary Actions:__** " + str(len(monster["legendary"])) + "\n")
    
    if return_monster:
        return {'monster': monster, 'string': discord_trim(''.join(monsterDesc))}
    else:
        return discord_trim(''.join(monsterDesc))

def searchSpell(spellname, serv_id='', return_spell=False):
    spellDesc = []
    with open('./res/spells.json', 'r') as f:
        contextualSpells = json.load(f)
    try:
        spell = next(item for item in contextualSpells if spellname.upper() == item["name"].upper())
    except Exception:
        try:
            spell = next(item for item in contextualSpells if spellname.upper() in item["name"].upper())
        except Exception:
            spellDesc.append("Spell does not exist or is misspelled (ha).")
            if return_spell: return {'spell': None, 'string': spellDesc}
            return spellDesc
    
    def parseschool(school):
        if (school == "A"): return "abjuration"
        if (school == "EV"): return "evocation"
        if (school == "EN"): return "enchantment"
        if (school == "I"): return "illusion"
        if (school == "D"): return "divination"
        if (school == "N"): return "necromancy"
        if (school == "T"): return "transmutation"
        if (school == "C"): return "conjuration"
        return school
    
    
    def parsespelllevel(level):
        if (level == "0"): return "cantrip"
        if (level == "2"): return level+"nd level"
        if (level == "3"): return level+"rd level"
        if (level == "1"): return level+"st level"
        return level+"th level"
    
    spell['level'] = parsespelllevel(spell['level'])
    spell['school'] = parseschool(spell['school'])
    spell['ritual'] = spell.get('ritual', 'no').lower()
    
    spellDesc.append("{name}, {level} {school}. ({classes})\n**Casting Time:** {time}\n**Range:** {range}\n**Components:** {components}\n**Duration:** {duration}\n**Ritual:** {ritual}".format(**spell))    
    
    if isinstance(spell['text'], list):
        for a in spell["text"]:
            if a is '': continue
            spellDesc.append(a.replace("At Higher Levels: ", "**At Higher Levels:** ").replace("This spell can be found in the Elemental Evil Player's Companion",""))
    else:
        spellDesc.append(spell['text'].replace("At Higher Levels: ", "**At Higher Levels:** ").replace("This spell can be found in the Elemental Evil Player's Companion",""))
  
    tempStr = '\n'.join(spellDesc)
    
    if return_spell:
        return {'spell': spell, 'string': discord_trim(tempStr)}
    else:
        return discord_trim(tempStr)