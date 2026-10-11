// YLine Pipeline Showcase Logic

const songData = {
    color: {
        metadata: {"artist": "Lotus Juice", "title": "Color Your Night", "album": "Persona 3 Reload", "year": 2024},
        lyrics: `[00:21.15] Time to shine and I'm down to ride
[00:23.39] I'm gonna drive until the break of dawn, wilding out
[00:26.02] I'm on a mission grinding out, whatever it is I gotta do
[00:28.56] Riding out until the day I meet you, I'm riding out
[00:31.27] I look up in the sky (sky)
[00:32.66] Asking lotta, why? (Why?)
[00:33.76] But never let it phase me, I'm keeping good vibes
[00:36.10] When I'm on the road, watch out for all surprises
[00:38.67] What it provides us
[00:39.63] Good and bad but nothing unties us
[00:41.00] Another wander in the night
[00:43.97] Let me paint the view
[00:46.65] Color a town with my light
[00:50.12] For every moment shared with you
[00:51.90] Not out in the day
[00:54.05] But never fully gone
[00:56.41] Going to be back again
[00:59.97] Until the coming of a dawn
[01:01.81] (Hey) for all the days ahead of us put your hands up
[01:04.86] Wave 'em side to side for good luck, ah
[01:06.98] (Hey) for all the nights like this, put your hands up
[01:10.19] Love the moment even from dusk, yup
[01:12.37] (Hey) you always got my back, and of course I got your back
[01:15.20] Don't you worry about that now
[01:17.13] (Hey) it's been a good day, good night
[01:19.51] It's gonna be a good day, good night
[01:21.70] 
[01:42.01] Two hands meet at zenith
[01:44.78] Nothing comes between us
[01:47.10] Dancing like ballerinas
[01:49.05] Under, the moonlight all night long
[01:52.35] How these plain and simple scenes
[01:54.45] Get painted so vividly by you
[01:59.25] I just wanna stay with you
[02:01.98] Around the world I slowly dance
[02:04.82] Whenever our eyes meet
[02:07.02] You know you leave me in a trance
[02:10.73] It means everything to me
[02:12.68] Looking down below
[02:14.73] The one I seek to find
[02:16.90] No matter where you might go
[02:20.82] Remember you'll be on my mind
[02:23.03] (Hey) always watching over me somehow you make me feel invincible
[02:26.28] Power to my soul, yup
[02:27.87] (Hey) I'm at ease with things that used to bother me
[02:30.55] 'Cause your existence just lights me up, yup
[02:33.19] (Hey) you always got my back, and of course I got your back
[02:36.13] Don't you worry about that now
[02:38.17] (Hey) it's been a good day, good night
[02:40.37] It's gonna be a good day, good night
[02:42.25] Within the inner heart I plead
[02:45.13] For you to talk to me
[02:47.35] I wanna hear all the good and bad
[02:50.24] The new stories you have
[02:52.50] As I drift across the sky
[02:55.36] The hour hand turns high
[02:57.27] So goodnight
[02:59.81] Let me sing a lullaby, love
[03:06.78] I'll be seeing you, baby
[03:09.65] `,
        images: [
            { src: "assets/images/color/img_000.jpg", prompt: "Time to shine and I'm down to  aesthetic" },
            { src: "assets/images/color/img_001.jpg", prompt: "I'm gonna drive until the brea aesthetic" },
            { src: "assets/images/color/img_002.jpg", prompt: "I'm on a mission grinding out, aesthetic" },
            { src: "assets/images/color/img_003.jpg", prompt: "Riding out until the day I mee aesthetic" },
            { src: "assets/images/color/img_004.jpg", prompt: "I look up in the sky (sky) aesthetic" },
            { src: "assets/images/color/img_005.jpg", prompt: "Asking lotta, why? (Why?) aesthetic" },
            { src: "assets/images/color/img_006.jpg", prompt: "But never let it phase me, I'm aesthetic" },
            { src: "assets/images/color/img_007.jpg", prompt: "When I'm on the road, watch ou aesthetic" },
            { src: "assets/images/color/img_008.jpg", prompt: "What it provides us aesthetic" },
            { src: "assets/images/color/img_009.jpg", prompt: "Good and bad but nothing untie aesthetic" },
            { src: "assets/images/color/img_010.jpg", prompt: "Another wander in the night aesthetic" },
            { src: "assets/images/color/img_011.jpg", prompt: "Let me paint the view aesthetic" },
            { src: "assets/images/color/img_012.jpg", prompt: "Color a town with my light aesthetic" },
            { src: "assets/images/color/img_013.jpg", prompt: "For every moment shared with y aesthetic" },
            { src: "assets/images/color/img_014.jpg", prompt: "Not out in the day aesthetic" },
            { src: "assets/images/color/img_015.jpg", prompt: "But never fully gone aesthetic" },
            { src: "assets/images/color/img_016.jpg", prompt: "Going to be back again aesthetic" },
            { src: "assets/images/color/img_017.jpg", prompt: "Until the coming of a dawn aesthetic" },
            { src: "assets/images/color/img_018.jpg", prompt: "(Hey) for all the days ahead o aesthetic" },
            { src: "assets/images/color/img_019.jpg", prompt: "Wave 'em side to side for good aesthetic" },
            { src: "assets/images/color/img_020.jpg", prompt: "(Hey) for all the nights like  aesthetic" },
            { src: "assets/images/color/img_021.jpg", prompt: "Love the moment even from dusk aesthetic" },
            { src: "assets/images/color/img_022.jpg", prompt: "(Hey) you always got my back,  aesthetic" },
            { src: "assets/images/color/img_023.jpg", prompt: "Don't you worry about that now aesthetic" },
            { src: "assets/images/color/img_024.jpg", prompt: "(Hey) it's been a good day, go aesthetic" },
            { src: "assets/images/color/img_025.jpg", prompt: "It's gonna be a good day, good aesthetic" },
            { src: "assets/images/color/img_026.jpg", prompt: "Two hands meet at zenith aesthetic" },
            { src: "assets/images/color/img_027.jpg", prompt: "Nothing comes between us aesthetic" },
            { src: "assets/images/color/img_028.jpg", prompt: "Dancing like ballerinas aesthetic" },
            { src: "assets/images/color/img_029.jpg", prompt: "Under, the moonlight all night aesthetic" },
            { src: "assets/images/color/img_030.jpg", prompt: "How these plain and simple sce aesthetic" },
            { src: "assets/images/color/img_031.jpg", prompt: "Get painted so vividly by you aesthetic" },
            { src: "assets/images/color/img_032.jpg", prompt: "I just wanna stay with you aesthetic" },
            { src: "assets/images/color/img_033.jpg", prompt: "Around the world I slowly danc aesthetic" },
            { src: "assets/images/color/img_034.jpg", prompt: "Whenever our eyes meet aesthetic" },
            { src: "assets/images/color/img_035.jpg", prompt: "You know you leave me in a tra aesthetic" },
            { src: "assets/images/color/img_036.jpg", prompt: "It means everything to me aesthetic" },
            { src: "assets/images/color/img_037.jpg", prompt: "Looking down below aesthetic" },
            { src: "assets/images/color/img_038.jpg", prompt: "The one I seek to find aesthetic" },
            { src: "assets/images/color/img_039.jpg", prompt: "No matter where you might go aesthetic" },
            { src: "assets/images/color/img_040.jpg", prompt: "Remember you'll be on my mind aesthetic" },
            { src: "assets/images/color/img_041.jpg", prompt: "(Hey) always watching over me  aesthetic" },
            { src: "assets/images/color/img_042.jpg", prompt: "Power to my soul, yup aesthetic" },
            { src: "assets/images/color/img_043.jpg", prompt: "(Hey) I'm at ease with things  aesthetic" },
            { src: "assets/images/color/img_044.jpg", prompt: "'Cause your existence just lig aesthetic" },
            { src: "assets/images/color/img_045.jpg", prompt: "(Hey) you always got my back,  aesthetic" },
            { src: "assets/images/color/img_046.jpg", prompt: "Don't you worry about that now aesthetic" },
            { src: "assets/images/color/img_047.jpg", prompt: "(Hey) it's been a good day, go aesthetic" },
            { src: "assets/images/color/img_048.jpg", prompt: "It's gonna be a good day, good aesthetic" },
            { src: "assets/images/color/img_049.jpg", prompt: "Within the inner heart I plead aesthetic" },
            { src: "assets/images/color/img_050.jpg", prompt: "For you to talk to me aesthetic" },
            { src: "assets/images/color/img_051.jpg", prompt: "I wanna hear all the good and  aesthetic" },
            { src: "assets/images/color/img_052.jpg", prompt: "The new stories you have aesthetic" },
            { src: "assets/images/color/img_053.jpg", prompt: "As I drift across the sky aesthetic" },
            { src: "assets/images/color/img_054.jpg", prompt: "The hour hand turns high aesthetic" },
            { src: "assets/images/color/img_055.jpg", prompt: "So goodnight aesthetic" },
            { src: "assets/images/color/img_056.jpg", prompt: "Let me sing a lullaby, love aesthetic" },
            { src: "assets/images/color/img_057.jpg", prompt: "I'll be seeing you, baby aesthetic" }
        ],
        videoSrc: "assets/videos/color.mp4?v=2"
    },
    panic: {
        metadata: {"artist": "Panic! at the Disco", "title": "London Beckoned Songs About Money Written by Machines", "album": "A Fever You Can't Sweat Out", "year": 2005},
        lyrics: `[00:01.02] Stop stalling, make a name for yourself
[00:03.16] Boy, you'd better put that pen to paper, charm your way out
[00:06.00] If you talk, you'd better walk, you'd better back your shit up
[00:08.89] With more than good hooks while you're all under the gun
[00:12.45] Start talking a sensationalist
[00:14.58] Oh, he's slightly clever to just a certain extent
[00:17.59] If you talk, you'd better walk, you'd better keep your mouth shut
[00:20.15] With more than good hooks while you're all under the gun
[00:26.84] (Panic!, meet the press)
[00:27.44] It's time for us to take a chance
[00:31.84] It's time for us to take a chance
[00:38.14] (Panic!, meet the press)
[00:40.38] It's time for us to take a chance
[00:42.94] It's time for us
[00:45.31] Well, we're just a wet dream for the webzine
[00:48.37] Make us it, make us hip, make us scene, or
[00:51.62] Shrug us off your shoulders
[00:52.82] Don't approve a single word that we wrote
[00:56.64] Well, we're just a wet dream for the webzine
[00:59.66] Make us it, make us hip, make us scene, or
[01:02.97] Shrug us off your shoulders
[01:04.19] Don't approve a single word that we wrote
[01:08.98] 
[01:11.89] I'm burning and I'm blacking my lungs
[01:13.72] Boy, you know it feels good with fire back on your tongue
[01:17.02] If you talk, you'd better walk, you'd better back your shit up
[01:19.48] With more than good hooks while you're all under the gun
[01:22.98] Start talking a sensationalist
[01:25.10] Oh, he's slightly clever to just a certain extent
[01:28.30] Oh, keep quiet, let us sing like the doves
[01:30.76] Then decide if it's done with purpose or lack thereof
[01:37.53] Just for the record
[01:38.96] The weather today is slightly sarcastic
[01:41.52] With a good chance of A, indifference
[01:43.65] And B, disinterest
[01:45.35] In what the critics say
[01:48.08] It's time for us to take a chance
[01:50.87] It's time for us
[01:53.16] Well, we're just a wet dream for the webzine
[01:56.17] Make us it, make us hip, make us scene, or
[01:59.46] Shrug us off your shoulders
[02:00.52] Don't approve a single word that we wrote
[02:04.31] Well, we're just a wet dream for the webzine
[02:07.45] Make us it, make us hip, make us scene, or
[02:10.74] Shrug us off your shoulders
[02:11.88] Don't approve a single word that we wrote
[02:16.71] 
[02:21.95] La-da-da-da-da-da-da-da
[02:23.89] La-da-da-da-da
[02:24.33] Ooh, whoa, ooh, whoa
[02:27.98] La-da-da-da-da-da-da-da
[02:29.43] La-da-da-da-da
[02:31.08] Ooh, whoa, ooh, whoa
[02:33.95] Just for the record
[02:35.33] The weather today is slightly sarcastic
[02:38.17] With a good chance of A, indifference
[02:40.18] And B, disinterest
[02:41.66] In what the critics say
[02:43.96] Well, we're just a wet dream for the webzine
[02:46.96] Make us it, make us hip, make us scene, or
[02:50.25] Shrug us off your shoulders
[02:51.36] Don't approve a single word that we wrote
[02:55.22] Well, we're just a wet dream for the webzine
[02:58.29] Make us it, make us hip, make us scene, or
[03:01.53] Shrug us off your shoulders
[03:02.75] Don't approve a single word that we wrote
[03:07.94] Just for the record
[03:09.48] The weather today is slightly sarcastic
[03:12.23] With a good chance of A, indifference
[03:14.52] And B, disinterest
[03:16.34] In what the critics say
[03:18.43] `,
        images: [
        { src: "assets/images/panic/img_000.jpg", prompt: "Stop stalling, make a name for aesthetic" },
        { src: "assets/images/panic/img_001.jpg", prompt: "Boy, you'd better put that pen aesthetic" },
        { src: "assets/images/panic/img_002.jpg", prompt: "If you talk, you'd better walk aesthetic" },
        { src: "assets/images/panic/img_003.jpg", prompt: "With more than good hooks whil aesthetic" },
        { src: "assets/images/panic/img_004.jpg", prompt: "Start talking a sensationalist aesthetic" },
        { src: "assets/images/panic/img_005.jpg", prompt: "Oh, he's slightly clever to ju aesthetic" },
        { src: "assets/images/panic/img_006.jpg", prompt: "If you talk, you'd better walk aesthetic" },
        { src: "assets/images/panic/img_007.jpg", prompt: "With more than good hooks whil aesthetic" },
        { src: "assets/images/panic/img_008.jpg", prompt: "(Panic!, meet the press) aesthetic" },
        { src: "assets/images/panic/img_009.jpg", prompt: "It's time for us to take a cha aesthetic" },
        { src: "assets/images/panic/img_010.jpg", prompt: "It's time for us to take a cha aesthetic" },
        { src: "assets/images/panic/img_011.jpg", prompt: "(Panic!, meet the press) aesthetic" },
        { src: "assets/images/panic/img_012.jpg", prompt: "It's time for us to take a cha aesthetic" },
        { src: "assets/images/panic/img_013.jpg", prompt: "It's time for us aesthetic" },
        { src: "assets/images/panic/img_014.jpg", prompt: "Well, we're just a wet dream f aesthetic" },
        { src: "assets/images/panic/img_015.jpg", prompt: "Make us it, make us hip, make  aesthetic" },
        { src: "assets/images/panic/img_016.jpg", prompt: "Shrug us off your shoulders aesthetic" },
        { src: "assets/images/panic/img_017.jpg", prompt: "Don't approve a single word th aesthetic" },
        { src: "assets/images/panic/img_018.jpg", prompt: "Well, we're just a wet dream f aesthetic" },
        { src: "assets/images/panic/img_019.jpg", prompt: "Make us it, make us hip, make  aesthetic" },
        { src: "assets/images/panic/img_020.jpg", prompt: "Shrug us off your shoulders aesthetic" },
        { src: "assets/images/panic/img_021.jpg", prompt: "Don't approve a single word th aesthetic" },
        { src: "assets/images/panic/img_022.jpg", prompt: "I'm burning and I'm blacking m aesthetic" },
        { src: "assets/images/panic/img_023.jpg", prompt: "Boy, you know it feels good wi aesthetic" },
        { src: "assets/images/panic/img_024.jpg", prompt: "If you talk, you'd better walk aesthetic" },
        { src: "assets/images/panic/img_025.jpg", prompt: "With more than good hooks whil aesthetic" },
        { src: "assets/images/panic/img_026.jpg", prompt: "Start talking a sensationalist aesthetic" },
        { src: "assets/images/panic/img_027.jpg", prompt: "Oh, he's slightly clever to ju aesthetic" },
        { src: "assets/images/panic/img_028.jpg", prompt: "Oh, keep quiet, let us sing li aesthetic" },
        { src: "assets/images/panic/img_029.jpg", prompt: "Then decide if it's done with  aesthetic" },
        { src: "assets/images/panic/img_030.jpg", prompt: "Just for the record aesthetic" },
        { src: "assets/images/panic/img_031.jpg", prompt: "The weather today is slightly  aesthetic" },
        { src: "assets/images/panic/img_032.jpg", prompt: "With a good chance of A, indif aesthetic" },
        { src: "assets/images/panic/img_033.jpg", prompt: "And B, disinterest aesthetic" },
        { src: "assets/images/panic/img_034.jpg", prompt: "In what the critics say aesthetic" },
        { src: "assets/images/panic/img_035.jpg", prompt: "It's time for us to take a cha aesthetic" },
        { src: "assets/images/panic/img_036.jpg", prompt: "It's time for us aesthetic" },
        { src: "assets/images/panic/img_037.jpg", prompt: "Well, we're just a wet dream f aesthetic" },
        { src: "assets/images/panic/img_038.jpg", prompt: "Make us it, make us hip, make  aesthetic" },
        { src: "assets/images/panic/img_039.jpg", prompt: "Shrug us off your shoulders aesthetic" },
        { src: "assets/images/panic/img_040.jpg", prompt: "Don't approve a single word th aesthetic" },
        { src: "assets/images/panic/img_041.jpg", prompt: "Well, we're just a wet dream f aesthetic" },
        { src: "assets/images/panic/img_042.jpg", prompt: "Make us it, make us hip, make  aesthetic" },
        { src: "assets/images/panic/img_043.jpg", prompt: "Shrug us off your shoulders aesthetic" },
        { src: "assets/images/panic/img_044.jpg", prompt: "Don't approve a single word th aesthetic" },
        { src: "assets/images/panic/img_045.jpg", prompt: "La-da-da-da-da-da-da-da aesthetic" },
        { src: "assets/images/panic/img_046.jpg", prompt: "La-da-da-da-da aesthetic" },
        { src: "assets/images/panic/img_047.jpg", prompt: "Ooh, whoa, ooh, whoa aesthetic" },
        { src: "assets/images/panic/img_048.jpg", prompt: "La-da-da-da-da-da-da-da aesthetic" },
        { src: "assets/images/panic/img_049.jpg", prompt: "La-da-da-da-da aesthetic" },
        { src: "assets/images/panic/img_050.jpg", prompt: "Ooh, whoa, ooh, whoa aesthetic" },
        { src: "assets/images/panic/img_051.jpg", prompt: "Just for the record aesthetic" },
        { src: "assets/images/panic/img_052.jpg", prompt: "The weather today is slightly  aesthetic" },
        { src: "assets/images/panic/img_053.jpg", prompt: "With a good chance of A, indif aesthetic" },
        { src: "assets/images/panic/img_054.jpg", prompt: "And B, disinterest aesthetic" },
        { src: "assets/images/panic/img_055.jpg", prompt: "In what the critics say aesthetic" },
        { src: "assets/images/panic/img_056.jpg", prompt: "Well, we're just a wet dream f aesthetic" },
        { src: "assets/images/panic/img_057.jpg", prompt: "Make us it, make us hip, make  aesthetic" },
        { src: "assets/images/panic/img_058.jpg", prompt: "Shrug us off your shoulders aesthetic" },
        { src: "assets/images/panic/img_059.jpg", prompt: "Don't approve a single word th aesthetic" },
        { src: "assets/images/panic/img_060.jpg", prompt: "Well, we're just a wet dream f aesthetic" },
        { src: "assets/images/panic/img_061.jpg", prompt: "Make us it, make us hip, make  aesthetic" },
        { src: "assets/images/panic/img_062.jpg", prompt: "Shrug us off your shoulders aesthetic" },
        { src: "assets/images/panic/img_063.jpg", prompt: "Don't approve a single word th aesthetic" },
        { src: "assets/images/panic/img_064.jpg", prompt: "Just for the record aesthetic" },
        { src: "assets/images/panic/img_065.jpg", prompt: "The weather today is slightly  aesthetic" },
        { src: "assets/images/panic/img_066.jpg", prompt: "With a good chance of A, indif aesthetic" },
        { src: "assets/images/panic/img_067.jpg", prompt: "And B, disinterest aesthetic" },
        { src: "assets/images/panic/img_068.jpg", prompt: "In what the critics say aesthetic" }
    ],
        videoSrc: "assets/videos/panic.mp4?v=1"
    },
    bad_days: {
        metadata: {"artist": "AJR", "title": "100 Bad Days", "album": "OK Orchestra", "year": 2017, "musicbrainz_id": "33b640c6-e84b-44bc-96c3-dfbb545898f5"},
        lyrics: `[00:04.10] Remember when we all got drunk
[00:07.18] I ended up with two broke thumbs
[00:10.67] Oh my god, I felt so dumb
[00:13.95] Lucky me
[00:17.20] I wrote a song that no one knows
[00:20.43] I played a show and no one showed
[00:24.04] Oh my god, I felt so alone
[00:27.26] Lucky me
[00:32.19] When all is going wrong
[00:34.18] And you're scared as hell
[00:38.90] Whatcha gonna do?
[00:40.39] Who you gonna tell?
[00:42.26] Maybe a hundred bad days
[00:44.94] Made a hundred good stories
[00:46.69] A hundred good stories
[00:47.99] Make me interesting at parties
[00:50.03] A hundred bad days
[00:51.60] Made a hundred good stories
[00:53.36] A hundred good stories
[00:54.89] Make me interesting at parties, yeah
[00:56.87] No, I ain't scared of you
[00:59.99] No, I ain't scared of you, no more
[01:03.74] (Da, da-da-da-da-da-da-da-da-da-da)
[01:06.71] (Da, da-da-da-da-da-da-da-da-da-da)
[01:10.31] No, I ain't scared of you
[01:13.49] No, I ain't scared of you, no more
[01:20.32] Remember when she broke my heart
[01:23.22] Waiting for the waiter to return my card
[01:27.30] Right as I let down my guard
[01:30.73] Lucky me
[01:33.85] We had to work a bit more hard
[01:36.40] Only just to get a little bit less far
[01:40.12] We could laugh about it all tomorrow
[01:43.92] Couldn't we?
[01:48.25] When all is going wrong
[01:50.02] And you're scared as hell
[01:55.06] Whatcha gonna do?
[01:56.80] Who you gonna tell?
[01:58.79] Maybe a hundred bad days
[02:01.55] Made a hundred good stories
[02:03.38] A hundred good stories
[02:04.69] Make me interesting at parties
[02:06.55] A hundred bad days
[02:07.94] Made a hundred good stories
[02:09.74] A hundred good stories
[02:11.54] Make me interesting at parties, yeah
[02:13.54] No, I ain't scared of you
[02:16.49] No, I ain't scared of you, no more
[02:20.04] (Da, da-da-da-da-da-da-da-da-da-da)
[02:23.21] (Da, da-da-da-da-da-da-da-da-da-da)
[02:26.97] No, I ain't scared of you
[02:30.12] No, I ain't scared of you no more
[02:44.82] (Screw your thing, it goes like this!)
[02:53.54] No, I ain't scared of you
[02:57.06] No, I ain't scared of you
[02:59.67] A hundred bad days
[03:01.09] Made a hundred good stories
[03:02.88] A hundred good stories
[03:04.42] Make me interesting at parties, yeah
[03:06.82] No, I ain't scared of you
[03:09.68] No, I ain't scared of you
[03:13.18] A hundred bad days
[03:14.70] Made a hundred good stories
[03:16.10] A hundred good stories
[03:17.86] Make me interesting at parties, yeah
[03:20.23] No, I ain't scared of you
[03:23.56] No, I ain't scared of you, no more
`,
        images: [
            { src: "assets/images/bad_days/img_000.jpg", prompt: "friends drinking beer" },
            { src: "assets/images/bad_days/img_001.jpg", prompt: "bandaged thumbs" },
            { src: "assets/images/bad_days/img_002.jpg", prompt: "head in hands" },
            { src: "assets/images/bad_days/img_003.jpg", prompt: "empty street" },
            { src: "assets/images/bad_days/img_004.jpg", prompt: "blank notebook" },
            { src: "assets/images/bad_days/img_005.jpg", prompt: "empty concert stage" },
            { src: "assets/images/bad_days/img_006.jpg", prompt: "solitary figure" },
            { src: "assets/images/bad_days/img_007.jpg", prompt: "abandoned car" },
            { src: "assets/images/bad_days/img_008.jpg", prompt: "chaotic mess" },
            { src: "assets/images/bad_days/img_009.jpg", prompt: "trembling hands" },
            { src: "assets/images/bad_days/img_010.jpg", prompt: "shrugging shoulders" },
            { src: "assets/images/bad_days/img_011.jpg", prompt: "whispering secrets" },
            { src: "assets/images/bad_days/img_012.jpg", prompt: "stormy sky" },
            { src: "assets/images/bad_days/img_013.jpg", prompt: "scattered polaroids" },
            { src: "assets/images/bad_days/img_014.jpg", prompt: "journal pages" },
            { src: "assets/images/bad_days/img_015.jpg", prompt: "party crowd" },
            { src: "assets/images/bad_days/img_016.jpg", prompt: "dark hallway" },
            { src: "assets/images/bad_days/img_017.jpg", prompt: "coffee stains" },
            { src: "assets/images/bad_days/img_018.jpg", prompt: "old letters" },
            { src: "assets/images/bad_days/img_019.jpg", prompt: "laughing friends" },
            { src: "assets/images/bad_days/img_020.jpg", prompt: "defiant face" },
            { src: "assets/images/bad_days/img_021.jpg", prompt: "shattered mirror" },
            { src: "assets/images/bad_days/img_022.jpg", prompt: "empty stage" },
            { src: "assets/images/bad_days/img_023.jpg", prompt: "empty stage" },
            { src: "assets/images/bad_days/img_024.jpg", prompt: "defiant face" },
            { src: "assets/images/bad_days/img_025.jpg", prompt: "shattered mirror" },
            { src: "assets/images/bad_days/img_026.jpg", prompt: "broken heart" },
            { src: "assets/images/bad_days/img_027.jpg", prompt: "restaurant table" },
            { src: "assets/images/bad_days/img_028.jpg", prompt: "lowered shield" },
            { src: "assets/images/bad_days/img_029.jpg", prompt: "lucky coin" },
            { src: "assets/images/bad_days/img_030.jpg", prompt: "heavy machinery" },
            { src: "assets/images/bad_days/img_031.jpg", prompt: "long winding road" },
            { src: "assets/images/bad_days/img_032.jpg", prompt: "friends laughing" },
            { src: "assets/images/bad_days/img_033.jpg", prompt: "empty chair" },
            { src: "assets/images/bad_days/img_034.jpg", prompt: "broken clock" },
            { src: "assets/images/bad_days/img_035.jpg", prompt: "shaking hands" },
            { src: "assets/images/bad_days/img_036.jpg", prompt: "question mark" },
            { src: "assets/images/bad_days/img_037.jpg", prompt: "phone call" },
            { src: "assets/images/bad_days/img_038.jpg", prompt: "calendar pages" },
            { src: "assets/images/bad_days/img_039.jpg", prompt: "photo album" },
            { src: "assets/images/bad_days/img_040.jpg", prompt: "book stack" },
            { src: "assets/images/bad_days/img_041.jpg", prompt: "crowd party" },
            { src: "assets/images/bad_days/img_042.jpg", prompt: "storm clouds" },
            { src: "assets/images/bad_days/img_043.jpg", prompt: "journal writing" },
            { src: "assets/images/bad_days/img_051.jpg", prompt: "standing tall silhouette" },
            { src: "assets/images/bad_days/img_061.jpg", prompt: "calendar pages" }
        ],
        videoSrc: "assets/videos/bad_days.mp4?v=22"
    },
    end: {
        metadata: {"artist": "Owl City", "title": "This Isn't the End", "album": "Mobile Orchestra", "year": 2015, "musicbrainz_id": "9cfa86cd-d0a4-412e-9ef0-7361835c16db"},
        lyrics: `[00:00.25] An eight-year-old girl had a panic attack
[00:06.54] 'Cause the father she loved left and never looked back
[00:13.45] No longer the hero she counted on
[00:20.14] He told her he loved her, and then he was gone
[00:26.40] She tried to look happy in front of her friends
[00:33.16] But knew that she'd never feel normal again
[00:39.57] She fought back the tears as they filled her eyes
[00:46.11] And wanted him back just to tell him goodbye
[00:52.08] When the rain falls down
[00:55.75] When it all turns around
[00:59.41] When the light goes out, this isn't the end
[01:07.74] Her dad was a good guy that everyone liked
[01:14.31] But nobody knew he was dying inside
[01:20.87] He promised his family he'd be alright
[01:27.49] And then with a gunshot, he left them behind
[01:33.39] When the rain falls down
[01:36.99] When it all turns around
[01:40.82] When the light goes out, this isn't the end
[01:48.13] When the rain falls down
[01:51.98] When it all turns around
[01:55.65] When the light goes out, this isn't the end, no
[02:04.04] The role of a father he never deserved
[02:10.30] He abandoned his daughter and never returned
[02:17.09] And over the years though the pain was real
[02:23.62] She finally forgave him and started to heal
[02:30.38] How close is the ending? Well, nobody knows
[02:36.75] The future's a mystery and anything goes
[02:43.52] Love is confusing and life is hard
[02:50.01] You fight to survive 'cause you've made it this far
[02:56.52] It's all too astounding to comprehend
[03:03.19] It's just the beginning, this isn't the end
[03:09.67] It's just the beginning, this isn't the end
`,
        images: [
            { src: "assets/images/end/img_000.jpg", prompt: "child trembling" },
            { src: "assets/images/end/img_001.jpg", prompt: "absent father silhouette" },
            { src: "assets/images/end/img_002.jpg", prompt: "empty superhero cape" },
            { src: "assets/images/end/img_003.jpg", prompt: "faded love letter" },
            { src: "assets/images/end/img_004.jpg", prompt: "forced smile group" },
            { src: "assets/images/end/img_005.jpg", prompt: "isolated girl shadows" },
            { src: "assets/images/end/img_006.jpg", prompt: "tears streaming face" },
            { src: "assets/images/end/img_007.jpg", prompt: "hand reaching goodbye" },
            { src: "assets/images/end/img_008.jpg", prompt: "heavy rain street" },
            { src: "assets/images/end/img_009.jpg", prompt: "spinning compass" },
            { src: "assets/images/end/img_010.jpg", prompt: "dark hallway" },
            { src: "assets/images/end/img_011.jpg", prompt: "smiling father" },
            { src: "assets/images/end/img_012.jpg", prompt: "empty medicine bottle" },
            { src: "assets/images/end/img_013.jpg", prompt: "family embrace" },
            { src: "assets/images/end/img_014.jpg", prompt: "smoking gun" },
            { src: "assets/images/end/img_015.jpg", prompt: "rainy window" },
            { src: "assets/images/end/img_016.jpg", prompt: "spinning compass" },
            { src: "assets/images/end/img_017.jpg", prompt: "flickering lights" },
            { src: "assets/images/end/img_018.jpg", prompt: "rainy window" },
            { src: "assets/images/end/img_019.jpg", prompt: "spinning compass" },
            { src: "assets/images/end/img_020.jpg", prompt: "dark hallway" },
            { src: "assets/images/end/img_021.jpg", prompt: "empty father's chair" },
            { src: "assets/images/end/img_022.jpg", prompt: "lonely swing set" },
            { src: "assets/images/end/img_023.jpg", prompt: "faded photograph" },
            { src: "assets/images/end/img_024.jpg", prompt: "blossoming garden" },
            { src: "assets/images/end/img_025.jpg", prompt: "foggy road" },
            { src: "assets/images/end/img_026.jpg", prompt: "starry sky" },
            { src: "assets/images/end/img_027.jpg", prompt: "tangled vines" },
            { src: "assets/images/end/img_028.jpg", prompt: "climbing rocky hill" },
            { src: "assets/images/end/img_029.jpg", prompt: "exploding brain" },
            { src: "assets/images/end/img_030.jpg", prompt: "sunrise horizon" },
            { src: "assets/images/end/img_031.jpg", prompt: "fresh sprout" }
        ],
        videoSrc: "assets/videos/end.mp4?v=22"
    },
    shelter: {
        metadata: {"artist": "Porter Robinson", "title": "Shelter", "album": "Worlds", "year": 2016, "musicbrainz_id": null},
        lyrics: `[00:38.75] I could never find the right way to tell you
[00:43.55] Have you noticed I've been gone?
[00:47.39] 'Cause I left behind the home that you made me
[00:52.94] But I will carry it along
[00:56.42] And it's a long way forward, so trust in me
[01:02.10] I'll give them shelter, like you've done for me
[01:06.55] And I know, I'm not alone, you'll be watching over us
[01:12.63] Until you're gone
[01:56.23] When I'm older, I'll be silent beside you
[02:00.55] I know words won't be enough
[02:05.18] And they won't need to know the names on our faces
[02:10.15] But they will carry on for us
[02:13.78] And it's a long way forward, so trust in me
[02:19.35] I'll give them shelter, like you've done for me
[02:23.14] And I know, I'm not alone, you'll be watching over us
[02:29.29] Until you're gone
[03:11.20] Oh it's a long way forward, trust in me
[03:16.26] I'll give them shelter, like you've done for me
[03:20.54] And I know, I'm not alone, you'll be watching over us
[03:26.91] Until
`,
        images: [
            { src: "assets/images/shelter/img_000.jpg", prompt: "empty mailbox" },
            { src: "assets/images/shelter/img_001.jpg", prompt: "empty chair" },
            { src: "assets/images/shelter/img_002.jpg", prompt: "abandoned house" },
            { src: "assets/images/shelter/img_003.jpg", prompt: "person with suitcase" },
            { src: "assets/images/shelter/img_004.jpg", prompt: "endless road" },
            { src: "assets/images/shelter/img_005.jpg", prompt: "open doorway" },
            { src: "assets/images/shelter/img_006.jpg", prompt: "guardian angel silhouette" },
            { src: "assets/images/shelter/img_007.jpg", prompt: "fading photograph" },
            { src: "assets/images/shelter/img_008.jpg", prompt: "elderly hand holding" },
            { src: "assets/images/shelter/img_009.jpg", prompt: "unwritten letter" },
            { src: "assets/images/shelter/img_010.jpg", prompt: "crowded street" },
            { src: "assets/images/shelter/img_011.jpg", prompt: "passing torch" },
            { src: "assets/images/shelter/img_012.jpg", prompt: "open road sunrise" },
            { src: "assets/images/shelter/img_013.jpg", prompt: "protective dome" },
            { src: "assets/images/shelter/img_015.jpg", prompt: "empty chair" },
            { src: "assets/images/shelter/img_016.jpg", prompt: "endless highway" },
            { src: "assets/images/shelter/img_017.jpg", prompt: "protective dome" },
            { src: "assets/images/shelter/img_019.jpg", prompt: "fading horizon" }
        ],
        videoSrc: "assets/videos/shelter.mp4?v=22"
    }
};

function loadSong(songKey, shouldScroll = true) {
    const data = songData[songKey];
    if (!data) return;

    // Update active button state
    document.querySelectorAll('.song-btn').forEach(btn => {
        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(`'${songKey}'`)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Render metadata as formatted JSON string
    const metaContainer = document.getElementById('out-metadata');
    if (metaContainer) {
        metaContainer.innerHTML = `<pre style="margin:0; padding:1rem; overflow-x:auto;">${JSON.stringify(data.metadata, null, 2)}</pre>`;
    }
    
    // Set current song title
    const titleEl = document.getElementById('current-song-title');
    if (titleEl) {
        titleEl.textContent = `${data.metadata.artist} - ${data.metadata.title}`;
    }

    // Render lyrics text
    const lyricsContainer = document.getElementById('out-lyrics');
    if (lyricsContainer) {
        lyricsContainer.textContent = data.lyrics;
    }
    
    const imgGrid = document.getElementById('out-images');
    if (imgGrid) {
        imgGrid.innerHTML = data.images.slice(0, 4).map(img => `
            <div class="img-card">
                <img src="${img.src}" alt="${img.prompt}">
                <div class="prompt-text">${img.prompt}</div>
            </div>
        `).join('');
    }

    const vid = document.getElementById('out-video');
    if (vid) {
        vid.src = data.videoSrc;
        vid.load();
    }

    const pipeline = document.getElementById('pipeline-container');
    if (pipeline) {
        pipeline.classList.remove('hidden');
    }
    
    if (shouldScroll) {
        setTimeout(() => {
            const step1 = document.getElementById('step1');
            if (step1) {
                step1.scrollIntoView({ behavior: 'smooth' });
            }
        }, 50);
    }
}

// Initialize on page load without auto-scrolling
window.addEventListener('DOMContentLoaded', () => {
    loadSong('color', false);
});

// Intersection Observer for Slide-In Animation
const steps = document.querySelectorAll('.step');
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('is-active');
        } else {
            entry.target.classList.remove('is-active');
        }
    });
}, { threshold: 0.2 });

steps.forEach(step => observer.observe(step));

// Back to Top Button
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', () => {
    if (window.scrollY > window.innerHeight) {
        backToTop.classList.add('visible');
    } else {
        backToTop.classList.remove('visible');
    }
});
backToTop.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});


// Scroll Tracker Logic
const scrollTracker = document.getElementById("scrollTracker");
const trackerNodes = document.querySelectorAll(".tracker-node");
const trackerLines = document.querySelectorAll(".tracker-line");
const sections = [
    document.querySelector(".hero"),
    document.getElementById("step1"),
    document.getElementById("step2"),
    document.getElementById("step3"),
    document.getElementById("step4")
];


let currentSectionIndex = 0;
function updateTracker() {
    const pipeline = document.getElementById("pipeline-container");
    if (!pipeline || pipeline.classList.contains("hidden")) {
        if (scrollTracker) scrollTracker.classList.remove("visible");
        return;
    }
    
    let bestIndex = -1;
    let minDistance = Infinity;
    const windowCenter = window.scrollY + window.innerHeight / 2;
    
    sections.forEach((s, index) => {
        if (!s) return;
        const rect = s.getBoundingClientRect();
        const sectionCenter = rect.top + window.scrollY + rect.height / 2;
        const distance = Math.abs(windowCenter - sectionCenter);
        if (distance < minDistance) {
            minDistance = distance;
            bestIndex = index;
        }
    });
    
    if (bestIndex !== -1 && bestIndex !== currentSectionIndex) {
        currentSectionIndex = bestIndex;
        
        if (currentSectionIndex === 0) {
            if (scrollTracker) scrollTracker.classList.remove("visible");
        } else {
            if (scrollTracker) scrollTracker.classList.add("visible");
        }

        trackerNodes.forEach(node => node.classList.remove("active"));
        trackerLines.forEach(line => line.classList.remove("active"));
        
        for (let i = 0; i <= currentSectionIndex; i++) {
            if (i < trackerNodes.length) trackerNodes[i].classList.add("active");
            if (i < currentSectionIndex && i < trackerLines.length) trackerLines[i].classList.add("active");
        }
    }
}

window.addEventListener("scroll", updateTracker);
window.addEventListener("resize", updateTracker);
// Initial check
setTimeout(updateTracker, 100);


trackerNodes.forEach(node => {
    node.addEventListener("click", () => {
        const targetClass = node.getAttribute("data-target");
        let targetEl;
        if (targetClass === "hero") targetEl = document.querySelector(".hero");
        else targetEl = document.getElementById(targetClass);
        if (targetEl) targetEl.scrollIntoView({ behavior: "smooth" });
    });
});

