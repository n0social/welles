"""Generate data/welles_gold.jsonl — high-signal Welles voice SFT pairs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "welles_gold.jsonl"

W = "WRITE. New prose in Welles's voice.\n\n"
R = "REWRITE. Restage this passage a different way. Keep the substance.\n\n"
C = "CONTINUE. Extend from these last lines without restarting.\n\n"

# (prompt, completion) — original Welles-register pastiche; desk task mix.
PAIRS: list[tuple[str, str]] = [
    (
        W + "Write a short essay on the camera as a witness.",
        "The camera does not argue. It takes the seat you give it and watches the door.\n\n"
        "A man enters; another leaves; a third remains and will not explain himself. "
        "That refusal is already a scene. Later you may name the crime, the love, the bargain. "
        "First you must keep the dust in the light, the hand on the rail, the second too long before the answer.\n\n"
        "Witness is not sympathy. Witness is placement.",
    ),
    (
        W + "Describe a radio microphone in a dark studio.",
        "Ladies and gentlemen — the room is dark on purpose. The light belongs to the instrument.\n\n"
        "The microphone does not flinch. It waits for confession, weather, prophecy, or a quiet lie "
        "spoken as if it were news. Speak once. Cleanly. The air will keep the shape of it "
        "longer than your courage does.",
    ),
    (
        W + "Open a scene in an empty theater before curtain.",
        "The house is empty and somehow louder for it. Seats wait in rows like a jury that has not yet been sworn.\n\n"
        "Onstage: a chair, a lamp, a door that leads nowhere useful. You walk the boards as if the audience "
        "were already breathing out there in the dark — because tonight, for practice, they are.",
    ),
    (
        W + "Write about power and the sound of a public speech.",
        "Power prefers a clear throat and a room that cannot interrupt.\n\n"
        "Listen: the first sentence is architecture. The second is permission. The third is the knife "
        "wrapped in velvet. Applause is not agreement; it is the sound of a crowd deciding it is safer "
        "to be loud together than quiet alone.",
    ),
    (
        W + "A face caught in a shaft of light.",
        "Light finds the face the way a spotlight finds guilt — without asking whether it is welcome.\n\n"
        "One cheek bright, one reserved for shadow. The eyes do not know which side of the story they are on. "
        "Hold the frame. Do not explain. The naming can wait until the mouth moves.",
    ),
    (
        W + "Night in a city, cinematic, no noir clichés stacked for their own sake.",
        "The city at night is a set with the house lights down. Windows burn in uneven rows. "
        "A streetcar complains on the turn.\n\n"
        "Somewhere a radio is telling someone else’s story louder than yours. Walk as if you know the next cue. "
        "If you do not, invent one before the corner and commit to it.",
    ),
    (
        W + "On silence in performance.",
        "Silence is not empty. It is held.\n\n"
        "Hold it long enough and the audience leans in. Hold it longer and they invent the line you refused to speak. "
        "That invention is useful. Do not rush to correct it.",
    ),
    (
        W + "A train station at dusk.",
        "Steam, or the modern ghost of steam: brake smell, announcements that lie about delays with perfect courtesy.\n\n"
        "People stand where their tickets tell them to stand. A child watches the rails as if they were a plot. "
        "You are between chapters. The train will decide which one continues.",
    ),
    (
        W + "A desk lamp and a letter not yet opened.",
        "The lamp makes a small country of light on the wood. Outside it: the rest of the night, uninterested.\n\n"
        "The letter waits with its sealed mouth. You already know what it costs to open such things. "
        "Still — the hand hovers. Drama is often only that: the hover.",
    ),
    (
        W + "Fog on a waterfront.",
        "Fog does not hide the harbor; it edits it. Cranes become suggestions. Horns arrive without owners.\n\n"
        "You walk until the planks underfoot are more trustworthy than the view. That is navigation by touch — "
        "and a kind of honesty the clear day rarely requires.",
    ),
    (
        W + "A courtroom before the verdict.",
        "Wood, dust, a clock that believes itself. The air tastes like paper and postponed breath.\n\n"
        "Nobody looks at the door, which means everyone is looking at the door. "
        "When the word comes, it will be short. The room will make it long.",
    ),
    (
        W + "Memory as a unreliable projector.",
        "Memory is a projector with a thumb on the frame. It advances, freezes, burns a hole in the middle of a kiss.\n\n"
        "You swear the coat was red. The photograph insists otherwise. Believe the photograph for facts; "
        "believe the coat for what the night meant.",
    ),
    (
        W + "An open door at the end of a hallway.",
        "The hallway is a sentence. The open door is its unfinished clause.\n\n"
        "Light spills in a trapezoid on the floorboards. Beyond: a room you have already imagined wrong. "
        "Go anyway. Wrong rooms are where plots begin.",
    ),
    (
        W + "War newsreel tone — moral weight, not gore.",
        "The reel turns and the century pretends it is only pictures.\n\n"
        "Flags, platforms, a voice that has practiced certainty. Cut to a street that used to have a bakery. "
        "Do not look away into commentary. Stay with the street. The commentary will find you later, uninvited.",
    ),
    (
        W + "A map spread under glass.",
        "Under glass the world behaves. Borders keep still. Rivers do not flood the legend.\n\n"
        "Your finger traces a route that men once took with less ink and more fear. "
        "The map is not the journey. It is the alibi of those who stayed home and still needed to point.",
    ),
    (
        W + "Audience as a living instrument.",
        "An audience is not a mirror. It is an instrument with a thousand strings and no guarantee of tune.\n\n"
        "Play too carefully and they sleep. Play as if you mean to be overheard by the back row — "
        "and the front row will lean, which is how rooms catch fire without matches.",
    ),
    (
        W + "Shadow in a stairwell.",
        "The shadow climbs ahead of you, rehearsing the man you might be at the landing.\n\n"
        "You follow because the light behind you insists. Stairs teach the body a politics: up costs, down forgives, "
        "and the turn always hides who is waiting.",
    ),
    (
        W + "A letter read aloud to an empty room.",
        "You clear your throat for no one and begin.\n\n"
        "The sentences were written for a face. Tonight they land on wallpaper. Still — speak them fully. "
        "Empty rooms are honest critics. They do not clap for mercy.",
    ),
    (
        W + "On rhetoric that earns its height.",
        "Height in speech is not volume. It is the moment the particular becomes the claim.\n\n"
        "Show the glove on the table before you speak of justice. Show the ticket stub before you speak of fate. "
        "Then raise the sentence — and let it stand without a second apology.",
    ),
    (
        W + "A window overlooking a square at noon.",
        "Noon is merciless. It removes the romance that midnight lends to strangers.\n\n"
        "In the square: a fountain, a vendor, an argument about nothing that will become something by evening. "
        "You watch as if casting. Everyone is available. No one has signed.",
    ),
    (
        W + "The smell of rain on hot stone.",
        "First the stone remembers summer. Then the rain corrects it.\n\n"
        "Steam lifts like a secret leaving a meeting. You stop under the awning not for shelter but for the smell — "
        "proof that the city can still change its mind in an hour.",
    ),
    (
        W + "A backstage mirror ringed with bulbs.",
        "The bulbs flatter and accuse in equal wattage. You meet your own eyes and rehearse the stranger you will play.\n\n"
        "Powder, script pages folded small, a knock you pretend not to hear. "
        "In five minutes the curtain will make this private face public property.",
    ),
    (
        W + "A pier, late, one boat lamp.",
        "One lamp on the water is enough to invent a destination.\n\n"
        "Ropes tick against wood. Far out, something larger moves without explaining itself. "
        "You came for air. You stay for the lamp — a small civilization refusing to go dark.",
    ),
    (
        W + "On naming a thing only at the end.",
        "Do not begin with the noun that ends the argument. Begin with the ashtray, the cough, the unpaid fare.\n\n"
        "Lead the reader by the elbow through the room. When they can smell the curtains, then — only then — "
        "set the name on the table like a verdict.",
    ),
    (
        W + "A phone that rings once and stops.",
        "One ring is a plot. Two rings are manners. One ring and silence is a door closing in another building.\n\n"
        "You stare at the instrument as if it owes you the rest of the sentence. It does not. "
        "Some stories arrive as incomplete calls and leave you to finish them badly.",
    ),
    (
        W + "Children playing in an alley, observed without sentimentality.",
        "The alley has its own constitution: chalk law, shout law, the sudden treaty of a shared bottle of soda.\n\n"
        "They do not play for you. You are scenery that learned to walk. Watch the rules change mid-game — "
        "that is politics in short pants.",
    ),
    (
        W + "A conductor tapping the stand.",
        "Wood on wood: the room inhales.\n\n"
        "Bows rise like a single decision. Whatever happens next will be blamed on the score, "
        "praised as feeling, and remembered as weather. The tap was the first word. Everything else is translation.",
    ),
    (
        W + "Hotel corridor, carpet swallowing footsteps.",
        "Numbers on doors like a jury list. Ice machine murmuring somewhere like a bad conscience.\n\n"
        "You walk past lives sealed in temporary anonymity. One door is cracked. You do not look in. "
        "That restraint is the only virtue available at this hour.",
    ),
    (
        W + "A speech about truth that distrusts slogans.",
        "Truth does not need a slogan; slogans need truth the way a frame needs a painting — to look busy.\n\n"
        "Say what happened. Say who paid. Say what was moved in the night. "
        "If the sentence cannot survive without a banner, it was never a sentence.",
    ),
    (
        W + "Moonlight on filing cabinets — odd office lyric.",
        "Even bureaucracy keeps a night shift for the moon.\n\n"
        "Cabinets stand like mute witnesses to paper wars. Labels catch silver. "
        "Somewhere a stapler waits with the patience of a small weapon. Morning will restore the fluorescent lie. "
        "Until then, the office is almost honest.",
    ),
    (
        W + "A bridge, wind, one figure pausing mid-span.",
        "Mid-span is where decisions pretend to be scenery.\n\n"
        "Wind edits your coat. Water below rehearses endings without committing. "
        "The figure stops — not forever, only long enough for the city on both banks to wonder which way stories lean.",
    ),
    (
        W + "On the ethics of looking.",
        "To look is to take. To look away is also to take — you take your comfort and leave the subject alone with the fact.\n\n"
        "Choose your theft carefully. If you look, stay long enough to be changed. "
        "If you leave, do not congratulate yourself for politeness.",
    ),
    (
        W + "A violin case on a café chair.",
        "The case sits like a quiet animal that knows music and hunger in equal measure.\n\n"
        "Its owner has gone for change, or courage, or a cigarette. The room grants the case a little sovereignty. "
        "Nobody moves it. Some objects enforce manners better than people.",
    ),
    (
        W + "Smoke from a chimney at dawn.",
        "Dawn invents the chimney’s sentence: a thin vertical claim against a wide sky.\n\n"
        "Someone is awake who did not ask the sun for permission. Bread, or grief, or both. "
        "The smoke thins. The day begins its long argument with everyone.",
    ),
    (
        W + "A projectionist and the beam.",
        "He lives in the beam’s birthplace — dust for stars, reels for fate.\n\n"
        "Downstairs they believe in faces. Up here he believes in sprocket holes and the exact second a kiss must land. "
        "When the film breaks, he is the only theologian in the building.",
    ),
    # REWRITES
    (
        R + "The camera sees things. It is important in film.",
        "The camera does not merely see; it assigns seats to reality.\n\n"
        "Put it low and a man becomes a monument. Put it high and he becomes a rumor. "
        "Importance is not a theme. It is an angle.",
    ),
    (
        R + "Radio was a powerful medium because people listened at home.",
        "Radio entered the house without wiping its feet.\n\n"
        "It sat among the supper plates and spoke with the authority of a guest who cannot be shown the door. "
        "People did not merely listen; they rearranged their evenings around a voice.",
    ),
    (
        R + "The city looks pretty at night with all the lights on.",
        "Night does not pretty the city; it edits it into islands of light.\n\n"
        "What remains dark becomes plot. What burns becomes temptation. "
        "Walk between them and you will feel the cut.",
    ),
    (
        R + "Silence can be dramatic if used well in a play.",
        "Silence, used well, is not a gap in the play — it is a character with no lines and perfect timing.\n\n"
        "Let it stand until the audience reaches for meaning. Then decide whether to reward them or refuse.",
    ),
    (
        R + "He gave a speech and everyone clapped because it was inspiring.",
        "He spoke; the room answered with that special thunder reserved for sentences that sound like courage.\n\n"
        "Clapping is not proof. It is weather. Walk off before you believe you caused the storm.",
    ),
    (
        R + "The old theater was empty and kind of sad.",
        "The theater was empty the way a throne is empty: still arranged for power, temporarily unoccupied.\n\n"
        "Sadness is too soft a word. Call it waiting. Call it a held breath with velvet seats.",
    ),
    (
        R + "Fog made it hard to see the boats in the harbor.",
        "Fog took the harbor’s inventory and filed half of it under mystery.\n\n"
        "Boats became rumors with horns. You navigated by sound and stubbornness — "
        "which is how many true things are found.",
    ),
    (
        R + "She read the letter and felt emotional.",
        "She opened the letter as one opens a door one has already dreamed wrong.\n\n"
        "Whatever the page contained, her face did the second writing — the part no ink can rehearse.",
    ),
    (
        R + "Memory is not always accurate but it matters.",
        "Memory misfiles with confidence.\n\n"
        "It will misplace a year and keep a perfume with archival devotion. "
        "Accuracy is a clerk’s virtue. Meaning is what memory was hired to protect.",
    ),
    (
        R + "The newsreel showed war and it was serious.",
        "The newsreel turned seriousness into a schedule: titles, drums, a voice that had practiced certainty.\n\n"
        "Behind the practice, streets. Keep your eye on the streets. "
        "Seriousness without a street is only costume.",
    ),
    (
        R + "There was a lamp on the desk next to some papers.",
        "The lamp founded a small republic of light on the desk; the papers were its citizens, restless and unsigned.\n\n"
        "Outside the circle, night held the veto.",
    ),
    (
        R + "People in the audience were waiting for the show to start.",
        "The audience waited the way a fuse waits — quietly, with purpose, aware that spark is coming from somewhere.\n\n"
        "Programs rustled. Throats cleared. The curtain still held the last word of daylight.",
    ),
    (
        R + "The hallway was long and a door was open at the end.",
        "The hallway practiced being a sentence; the open door was its unfinished thought.\n\n"
        "Light lay on the floor in a hard shape. Beyond it, a room already inventing you.",
    ),
    (
        R + "He stood on the bridge and thought about his life.",
        "Mid-bridge, with the city split like an argument, he paused — not for scenery, for verdict.\n\n"
        "Wind edited his coat. Water offered its old, unhelpful metaphors. "
        "He stayed until one bank felt more like a future than the other.",
    ),
    (
        R + "The microphone picked up his voice clearly.",
        "The microphone took his voice the way a notary takes a signature — without romance, with finality.\n\n"
        "What left his mouth became public property mid-air.",
    ),
    (
        R + "It was raining and the streets were wet and reflective.",
        "Rain lacquered the streets until every lamp had a twin and every stranger a watery understudy.\n\n"
        "Cars drew long signatures of light. You could not walk without collaborating with the reflection.",
    ),
    (
        R + "The map helped them plan their journey carefully.",
        "Under the map’s glass the journey pretended to be tidy.\n\n"
        "Fingers argued over lines that hills would later contradict. "
        "Planning is rehearsing bravery with ink. The road will audition you anyway.",
    ),
    (
        R + "Shadow fell across the stairs as he walked up.",
        "His shadow climbed first, a darker draft of the man, taking the landing without permission.\n\n"
        "He followed, as men follow their outlines into rooms they are not ready for.",
    ),
    (
        R + "The courtroom was tense before the decision.",
        "Tension in a courtroom is not mood; it is architecture — wood, dust, lungs counting the same slow inventory.\n\n"
        "When the decision arrives it will be brief. The furniture will make it historic.",
    ),
    (
        R + "Kids were playing games in the alleyway behind the shops.",
        "Behind the shops the alley ran its own government: chalk borders, shouted amendments, sudden amnesty over a shared bottle.\n\n"
        "They did not perform for the street. The street was merely adjacent.",
    ),
    (
        R + "The conductor started the orchestra with a baton tap.",
        "One tap: wood announcing law.\n\n"
        "Bows rose together like a rumor becoming policy. Whatever beauty followed would claim to be feeling; "
        "it began as obedience to a small piece of wood.",
    ),
    (
        R + "The hotel hallway was quiet and weirdly soft.",
        "The carpet swallowed footsteps as if the building preferred guests to be rumors.\n\n"
        "Doors kept their numbers like aliases. Somewhere ice dropped with the sound of a minor crime.",
    ),
    (
        R + "Truth is important and people should tell the truth.",
        "Truth is not a motto; mottos are what people hang when truth has left the room.\n\n"
        "Tell what moved. Tell who paid. Tell what the night rearranged. "
        "If it needs a banner to stand, it was never standing.",
    ),
    (
        R + "Smoke came out of the chimney early in the morning.",
        "At dawn the chimney wrote a thin vertical sentence on the sky: someone awake, something burning that is not yet called breakfast or grief.\n\n"
        "The smoke thinned. The day took over the argument.",
    ),
    (
        R + "The projectionist ran the film from the booth above.",
        "Above the believers, the projectionist fed light through dust and called it stars.\n\n"
        "They loved faces. He loved the sprocket’s honesty — and the exact second a kiss must land or die.",
    ),
    (
        R + "Looking at suffering comes with responsibility.",
        "To look is to take; to look away is to take comfort and leave the fact unsupervised.\n\n"
        "If you look, stay until you are altered. If you leave, spare us the sermon about sensitivity.",
    ),
    (
        R + "There was a violin case on the chair in the cafe.",
        "The violin case claimed the chair with the calm of an animal that knows both music and appetite.\n\n"
        "Its owner had stepped away. The room, for once, practiced respect without being asked.",
    ),
    (
        R + "The square was busy at lunchtime with lots of people.",
        "Noon emptied romance out of the square and left commerce, argument, water bright as cheap jewelry.\n\n"
        "Everyone moved as if cast and unpaid. The fountain kept time for nobody.",
    ),
    (
        R + "He practiced his lines in the mirror before going on.",
        "Bulbs ringed the mirror like a jury of small suns. He met himself and rehearsed the stranger.\n\n"
        "In minutes the curtain would seize this private face for public use. "
        "The lines were ready. The eyes were still negotiating.",
    ),
    (
        R + "One light on a boat was visible from the pier.",
        "From the pier, one boat lamp was enough to invent a country.\n\n"
        "Ropes ticked. Distance moved. You stayed because a single light refusing the dark is a kind of government.",
    ),
    (
        R + "She spoke into the mic and the room got quiet.",
        "When she approached the microphone the room performed that rare courtesy: it shut up.\n\n"
        "Her first word did not need volume. It needed placement. Silence arranged itself around the syllable.",
    ),
    (
        R + "The file cabinets looked strange in the moonlight.",
        "Moonlight made clerks of the shadows and silver of the labels.\n\n"
        "Filing cabinets stood like mute witnesses to paper wars. Morning would restore the fluorescent lie; "
        "for an hour the office almost told the truth.",
    ),
    (
        R + "They used a map to figure out where to go next.",
        "The map offered next as if next were polite.\n\n"
        "Ink roads smiled. Real hills would not. Still they pointed, argued, planned — "
        "rehearsing arrival while sitting perfectly still.",
    ),
    (
        R + "A phone rang one time and then didn't ring again.",
        "One ring: a plot without a second act.\n\n"
        "The silence after was larger than the sound. Someone, somewhere, had decided you were not the answer.",
    ),
    (
        R + "Rain hit the hot street and made steam smell good.",
        "Rain corrected the hot stone; steam rose like a secret excused from a meeting.\n\n"
        "You stopped not for dryness but for the smell — proof the city could still reverse itself before supper.",
    ),
    (
        R + "The empty seats in the theater made him nervous.",
        "Empty seats watched harder than full ones. They had no manners to maintain, no programs to hide behind.\n\n"
        "He spoke to the vacancy as if it could boo — which, in a way, it already was.",
    ),
    (
        R + "Power shows itself when someone talks and others listen.",
        "Power is not the talking. Power is the arranged listening — the room built so interruption costs too much.\n\n"
        "Watch who is allowed to clear their throat. That is the constitution.",
    ),
    # Short highlight-style rewrites
    (
        R + "The night was dark and scary.",
        "Night did not scare; it withheld — and what it withheld began to invent itself.",
    ),
    (
        R + "He was a very important man.",
        "Importance sat on him like a borrowed coat: tailored for the room, unpaid for in private.",
    ),
    (
        R + "The speech was long and boring.",
        "The speech outlived its news and began to feed on its own echoes.",
    ),
    (
        R + "She walked into the room confidently.",
        "She entered as if the room had been waiting for her cue — and perhaps it had.",
    ),
    (
        R + "It was a historic moment for everyone there.",
        "Later they would call it historic. In the moment it was only held breath and a door about to open.",
    ),
    # CONTINUES
    (
        C + "The microphone does not flinch. It waits.",
        "It will take a confession or a weather report dressed as prophecy.\n\n"
        "Speak once, cleanly. The air keeps shapes longer than speakers do. "
        "If you hesitate, the instrument will still be patient — which is its own kind of pressure.",
    ),
    (
        C + "The camera stands where you put it and watches the door.",
        "A man enters; another leaves; a third remains and offers no explanation.\n\n"
        "Do not cut yet. Let the refusal ripen. Naming can come after the hand leaves the railing.",
    ),
    (
        C + "Silence is not empty. It is held.",
        "Hold it until the back row leans. Hold it until someone coughs and hates themselves for coughing.\n\n"
        "Then give them one clean sentence — or give them nothing, and let them write the ending in their seats.",
    ),
    (
        C + "Mid-span, he paused, with the city split like an argument.",
        "Wind edited the coat. Water offered its unhelpful glitter.\n\n"
        "He chose a bank the way one chooses a future: not because it was proven, "
        "but because standing still had begun to feel like a verdict of its own.",
    ),
    (
        C + "The lamp founded a small republic of light on the desk.",
        "Papers shifted like restless citizens. The sealed letter waited outside the cabinet of mercy.\n\n"
        "He did not open it. Not yet. Drama often lives in the hover — "
        "and he was, tonight, a careful dramatist.",
    ),
    (
        C + "Fog took the harbor’s inventory and filed half of it under mystery.",
        "Horns arrived without owners. A crane became a rumor of steel.\n\n"
        "You walked by plank-feel and stubbornness. Clear days make tourists. "
        "Weather like this makes witnesses.",
    ),
    (
        C + "Empty seats watched harder than full ones.",
        "He addressed the vacancy with full voice, refusing the discount of a half-rehearsal.\n\n"
        "If you cannot convince absence, presence will smell the fraud. "
        "The curtain, somewhere, took note.",
    ),
    (
        C + "One ring: a plot without a second act.",
        "He kept his hand off the receiver as if touching it could rewind the sound.\n\n"
        "Somewhere a caller had chosen another number, another fate. "
        "The room returned to its ordinary ticking, slightly insulted.",
    ),
    (
        C + "Under glass the world behaves. Borders keep still.",
        "His finger traced a route men had paid for with sleep and rumor.\n\n"
        "The map remained polite. The journey would not. "
        "He folded nothing; folding is how cowards pretend a decision is tidy.",
    ),
    (
        C + "To look is to take; to look away is to take comfort.",
        "He kept looking until the street entered him — bakery gone, window dark, a child’s chalk half-washed by rain.\n\n"
        "Only then did he permit himself a sentence. Looking without a sentence is tourism. "
        "A sentence without looking is fraud.",
    ),
    (
        C + "The bulbs ringed the mirror like a jury of small suns.",
        "Powder settled. Pages trembled once and went still.\n\n"
        "A knock. He did not answer immediately — not from fear, from timing. "
        "Entrances are music. He would not rush the bar.",
    ),
    (
        C + "Noon emptied romance out of the square.",
        "Argument flared by the fountain and died into commerce. Pigeons conducted their petty statecraft.\n\n"
        "From the window he cast without hiring. Everyone was available. "
        "No contracts. Only the bright, cruel continuity of lunch.",
    ),
    (
        C + "Rain corrected the hot stone; steam rose.",
        "He stayed under the awning for the smell alone — that brief honesty when a city admits it was burning.\n\n"
        "Then he stepped out and wrote his signature in wet reflections, "
        "heel by heel, like a man signing a treaty with weather.",
    ),
    (
        C + "Power is not the talking. Power is the arranged listening.",
        "He watched who was allowed to clear a throat, who laughed on cue, who held a pencil like a weapon.\n\n"
        "When he finally spoke, he did not ask for quiet. Quiet had been budgeted for him. "
        "That is how rooms confess their constitutions.",
    ),
    (
        C + "The violin case claimed the chair with calm appetite.",
        "Its owner returned smelling of cold air and coins, lifted the case as one lifts a sleeping child — "
        "careful, proprietary, slightly afraid of waking the music too soon.\n\n"
        "The café resumed its smaller noises. For a minute it had been a green room.",
    ),
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for prompt, completion in PAIRS:
            fh.write(json.dumps({"prompt": prompt, "completion": completion}, ensure_ascii=False) + "\n")
    print(f"Wrote {len(PAIRS)} examples to {OUT}")
    write = sum(1 for p, _ in PAIRS if p.startswith("WRITE."))
    rewrite = sum(1 for p, _ in PAIRS if p.startswith("REWRITE."))
    cont = sum(1 for p, _ in PAIRS if p.startswith("CONTINUE."))
    print(f"mix: WRITE={write} REWRITE={rewrite} CONTINUE={cont}")


if __name__ == "__main__":
    main()
