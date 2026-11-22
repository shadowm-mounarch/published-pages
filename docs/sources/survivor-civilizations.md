# Survivor civilizations

## Integration design

| Existing owner | Integration |
| --- | --- |
| HordeRegistry, Horde and Migration | Read dimension, position and surviving strength during scheduled strategic updates. The migration engine continues to own zombies. |
| Settlements and VillagerHelpers | Ordinary village economies and the player settlement keep their current ownership. Managed expedition villagers use a separate population ledger. |
| Soldier and TaCZ | Faction guards use the campaign soldier entity with faction-specific allegiance, targeting and specialization. Campaign roster slots remain reserved for campaign encounters. |
| Recruit, SquadData and Recruiting | Enlistment transfers a named individual to the player's squad and uses the recruit's existing progression and healing. |
| CampaignData, CampaignSites and SiteData | Discover existing strategic sites from campaign facts. Campaign blocks, objectives and campaign garrisons retain their existing lifecycle. |
| Minimap and DeadSiegeNetwork | Physical actors use normal entity tracking. The existing minimap snapshot assigns visible survivors a marker based on the viewing player’s relationship with them. Leader interactions use server-authoritative chat commands. |

CivilizationData owns one overworld ledger. A person has one UUID and at most one current mission or captor. Population, active defenders and available personnel are derived from that roster. Territory is owned by site, and a diplomatic agreement is keyed by an unordered faction pair. Operations reserve people and debit supplies before departure. Leader succession selects a surviving free member.

A persisted strategic clock advances every 100 server ticks. Economic and diplomatic decisions run every 2,400 simulation ticks. Travel interpolates between recorded coordinates without consulting terrain in unloaded chunks. Nearby representation requires an already loaded chunk, a safe surface and an available entity slot. Physical combat and abstract resolution share the same mission and casualty ledger. Versioned persistence includes identities, cargo, relationships, mission progress and entity snapshots. Existing saves begin with an empty civilization ledger.

Balance and compatibility risks include competing AI target rules, player recruitment during an operation, stale chunk entities after a restart, two players observing one operation, overlapping horde damage and siege resolution, and the number of loaded representatives. Test these at ownership transitions as well as in a quiet world.

## Playing

Look for named survivors around overworld camps, patrols and supply convoys. Right-click a survivor to open their conversation in chat. Each action checks proximity, line of sight, faction standing and current eligibility again on the server.

- Hold food and choose **Supply** to build trust. Honey bottles and golden apples contribute medical supplies.
- Hold an emerald and choose **Trade** at a settlement or convoy to purchase bread from its stock.
- At 10 reputation, an eligible survivor can join your squad. Refugees can join immediately if your squad has room. The recruit keeps their name, experience and equipped gear.
- Speak to a leader at 30 reputation to negotiate protection or an alliance. Allied leaders can dispatch relief to the campaign refuge. Killing zombies near a settlement builds reputation. Attacking residents damages it.
- Refugees displaced by hunger or hordes can wait at the campaign refuge for one Minecraft day. Accept individuals, give provisions, redirect them or escort them to another settlement. An escorted party pauses when its guide falls behind or disconnects.
- Captured personnel retain their roster identity and progression. Approach a prisoner to attempt a rescue, or negotiate with the holding faction. A reciprocal exchange requires a prisoner on both sides.
- To occupy a cleared installation for an ally, stand inside it and use `/faction capture <allied-faction-uuid>`. The server checks standing, territory ownership, war status and remaining defenders.

## Administration and diagnostics

Operators can use `/faction list`, `info`, `locate` and `territory` to inspect the ledger. `/faction create <type>` founds a faction at the command position. The six types are `remnants`, `settlers`, `raiders`, `scavengers`, `researchers` and `mercenaries`.

Use `/faction relation <a> <b>` to inspect a pair. The same argument order works with `war`, `peace`, `alliance`, `protection`, `betray`, `cede` and `exchange`. Use `/military operation <a> <b>` after declaring war. `/military status <a>` reports active missions, remaining travel time, casualties and history. `/survivor spawn <count>` creates a new group. `/survivor relocate <id>` dispatches refugees toward the operator's location. Simulation commands queue bounded increments on the server thread.

World-specific settings live in `serverconfig/deadsiege-civilizations.toml`. Activation and deactivation radii, physical population cap, maximum patrol size and role selection priorities are configurable. A patrol priority of zero excludes that specialization from patrols. Supplies in the status output are ordered food, ammunition, medicine, materials, weapons and fuel.

## Verification

- Run `gradlew.bat --offline build` for the release jar and build checks.
- Run `gradlew.bat --offline -I tools/campaign-test.init.gradle runGameTestServer` for the complete Forge suite, including physical ownership, two observers, refugee migration, convoys, conquest and concurrent wars with 2,048 initial residents.
- Run `tools/test-civilization-restart.ps1` to create two factions, dispatch an assault and verify its identity, diplomacy and roster across three dedicated-server launches.
- Run `tools/play.ps1 -Hidden -VerificationScenario civilization -VerificationDirectory build/packaged-civilization` to exercise the packaged mod with the client and TaCZ. The client writes its verdict to `client-test-result.txt` in that verification directory. Install matching 0.4.0 builds on clients and servers. Protocol 16 includes the synchronized faction-soldier flag used by the minimap.
