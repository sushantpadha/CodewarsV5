# Ideas

1. Deck (and making strategy baesd on them)

## Major differences from Clash Royale
1. No buildings (so Giant is stronger)
2. Larger arena (so stacking stronger attacks is better)
3. " " (so sudden close deployments dont work, every attack must be layered)

Note:
0.05 / frame for first 120s
0.1 / frame for last 60s

## Deck

Im thinking of building a strategy based on the deck.

Alternatively, build a deck-agnostic strategy and then loop over all decks to optimize? (seems harder)

### Deck A
```
Giant (5) – Primary tank to soak damage.
Musketeer (4) – High single-target DPS, covers air.
Wizard (5) – Splash support behind Giant, covers swarms.
Archer (3) – Additional ranged DPS, flexible.
Knight (3) – Mini-tank or secondary tank in defense.
Minions (3) – Air troop for quick takedown of ground-targeting enemies.
Skeletons (1) – Cheap cycle, distraction, or finishing off big targets with a swarm.
Valkyrie (4) – Ground splash for defending swarms or supporting pushes.

Total Elixir: 5 + 4 + 5 + 3 + 3 + 3 + 1 + 4 = 28
Average Elixir: 3.5
```

1. Giant for pushing attack OR distraction as tank
2. Valkyrie + Wizard offer high and splash dmg
3. Skeleton support and distract
4. Solid air defense troops

## Extras

Implement enemy elixir counting and card counting to anticipate next move.

## Strategy

```text
################## Early Game ############################
    [ Play defensive troops to gauge enemy's deck.
	  and figure out his *WIN CONDITION*     ]
	                  / \
					/     \
    [ defend if attacked ]   \
	                [ try for chip damage only at this point ]

Note counter if we have any for enemy's win condition and keep it handy!


################ Mid Game ######################
             [ same as before ]
			        ||
(when high on elixir | enemy weak | enemy lacks counter)
		            ||
					\/
        [ deploy win condition ]

	else:
	[ try to add more supporting troops ]


#######################################################
Win Condition: 	Giant
Support: 		Wizard / Valkyrie + Archer + Muskeeter
Defense: 		Wizard + Valkyrie + Archer + Knight + Muskeeter
Distract: 		Skeleton + Knight
```