# 02-Text-Adventure
A text-based adventure game.
To play, run the game using python; e.g. `python main.py`.
You need Python 3.7 or later to play.

## How to play
When you start the game, the game will ask you to pick a class. Enter a number to pick the class that corresponds to that number. Each class starts with different stats and items.

During gameplay, you can interact with objects around you. For example, you can type 'look door' to look at a door. If you are engaged in combat, you can inspect your enemies; for example, if you are fighting a spider, you can type 'look spider'. You can also see what items are in your inventory by entering 'inventory' and you can see more information about stats by typing 'stats'.

While you are out of combat, you can move around the game world with the 'move' command. The game will tell you what locations are available to you. Here is an example:
```
There are 2 exits:
    0. SOUTH:   Forest entrance
    1. NORTH:   ???
```
You can type 'move south' to go to the forest enterance, or you can type 'move north' to go into an unknown area.

At any time, you can use an item with the 'use' command. After typing 'use', you will be shown a list of items you can use. Enter the number corresponding to the item you want to use, or type 'cancel' to cancel.

In combat, you will always go first. You can enter 'attack' to attack an enemy, or 'use' to use an item. After using either of these commands, the enemies will make their attack. If you use an attack, you will be shown a list of attacks you can perform. Enter the number corresponding to the attack you want to use. For example, as a cleric, you get the following attacks:
```
> attack
    1. Unarmed attack [STR] - deals 2 damage
    2. strike (Staff) [STR+2] - deals 2 damage
    3. cast (Smiting spell) [SOUL+1] - deals 3 holy damage
Choose an attack [or 'cancel' to cancel]: 
```
The value in brackets is how many dice you roll to perform that attack. For example, a cleric has three maximum strength, so if they are at full strength and decide to use their staff to attack, they will roll 5d6 to attack. In turn, the enemy will roll a defense roll. An enemy might, for example, roll 4d6 to defend themselves from your attack. If your roll is greater than or equal the enemy's roll, then you hit them. Once an enemy takes enough damage, they will die.

On the enemyies' turn, each enemy will make an attack. For example, an enemy might decide to bite you, which would deal 1 STR damage if it hits, and might roll 3d6 to make their attack. You then get to choose how you want to defend yourself; for example, the cleric gets the following options:
```
The spider attempts to bite you.
The Massive Spider is rolling 3d6 to attack...
The Massive Spider rolled [3 1 5] = 9
    1. cast (Divine Protection) [SOUL+2]
    2. Dodge [DEX]
Choose a reaction:
```
A cleric could cast divine protection, which if they have 4 SOUL, would give them 6d6 to defend, or they could use dodge, which if they have 2 DEX, would give them 2d6 to defend. If the enemy rolls higher on their attack than you roll on your defense, then you take 1 damage to whichever stat they were targetting. For example, the bite attack would deal one damage to your STR.

If you run out of any stat, then your game immediately ends. The rolls that you make for each stat depend on how much of that stat you have left, NOT the maximum value. If you see a `-` before a stat, then your roll increases when you have less of that stat; e.g. if you see `-SOUL` on an attack, then that attack will roll more dice the less SOUL you have.