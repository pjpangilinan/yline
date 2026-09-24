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
    take_me_dancing: {
        metadata: {"artist": "Will Joseph Cook", "title": "Take Me Dancing", "album": "Sweet Jelly Roll", "year": 2016},
        lyrics: `[00:01.74] Here's to Julian, a man among a million others
[00:06.88] Turned his back upon it all
[00:12.57] Raise another glass then smash it up into its fragments
[00:18.65] Walking barefoot on the ground
[00:23.09] And as I fall into the bottle bank (broken glass)
[00:29.03] You can make me into anything
[00:32.07] As long as I'm reflecting you
[00:35.16] Lonely is your love
[00:37.85] I could be the answer to
[00:41.03] All of your prayers
[00:44.65] Take me dancing
[00:46.94] Lonely ain't enough
[00:49.50] I could be the answer to
[00:52.66] All of your prayers
[00:56.37] Take me dancing
[00:59.21] Sing to Emily, make her laugh and talk her accent
[01:05.58] See the colour in her eyes
[01:11.06] Then you'll take her palm and joke about a life together
[01:17.11] Lying, smoking on the ground
[01:21.43] And as I fall into the bottle bank (broken glass)
[01:27.61] You can make me into anything
[01:30.67] As long and I'm reflecting you
[01:33.79] Lonely is your love
[01:36.49] I could be the answer to
[01:39.49] All of your prayers
[01:43.22] Take me dancing
[01:45.33] Lonely ain't enough
[01:48.18] I could be the answer to
[01:51.15] All of your prayers
[01:54.84] Take me dancing
[01:57.20] Every moment (every moment)
[02:03.19] Always like this (always like this)
[02:08.52] We've got our come ups
[02:11.48] (We've got our come ups)
[02:14.06] And your dirty mind
[02:20.62] Lonely is your love
[02:23.21] I could be the answer to
[02:26.22] All of your prayers
[02:30.20] Take me dancing
[02:32.27] Lonely ain't enough
[02:35.16] I could be the answer to
[02:38.14] All of your prayers
[02:41.62] Take me dancing
[02:43.85] We could walk to the shitty bars and
[02:46.80] We could swing to Americana
[02:49.88] I don't have much, don't make a difference, just
[02:53.56] Take me dancing
[02:55.78] We could walk to the shitty bars and
[02:58.64] We could swing to Americana
[03:01.38] I don't have much, don't make a difference, just
[03:05.12] Take me dancing`,
        images: [
            { src: "assets/images/take_me_dancing/img_000.jpg", prompt: "Here's to Julian, a man among " },
            { src: "assets/images/take_me_dancing/img_001.jpg", prompt: "Turned his back upon it all" },
            { src: "assets/images/take_me_dancing/img_002.jpg", prompt: "Raise another glass then smash" },
            { src: "assets/images/take_me_dancing/img_003.jpg", prompt: "Walking barefoot on the ground" },
            { src: "assets/images/take_me_dancing/img_004.jpg", prompt: "And as I fall into the bottle " },
            { src: "assets/images/take_me_dancing/img_005.jpg", prompt: "You can make me into anything" },
            { src: "assets/images/take_me_dancing/img_006.jpg", prompt: "As long as I'm reflecting you" },
            { src: "assets/images/take_me_dancing/img_007.jpg", prompt: "Lonely is your love" },
            { src: "assets/images/take_me_dancing/img_008.jpg", prompt: "I could be the answer to" },
            { src: "assets/images/take_me_dancing/img_009.jpg", prompt: "All of your prayers" },
            { src: "assets/images/take_me_dancing/img_010.jpg", prompt: "Take me dancing" },
            { src: "assets/images/take_me_dancing/img_011.jpg", prompt: "Lonely ain't enough" },
            { src: "assets/images/take_me_dancing/img_012.jpg", prompt: "I could be the answer to" },
            { src: "assets/images/take_me_dancing/img_013.jpg", prompt: "All of your prayers" },
            { src: "assets/images/take_me_dancing/img_014.jpg", prompt: "Take me dancing" },
            { src: "assets/images/take_me_dancing/img_015.jpg", prompt: "Sing to Emily, make her laugh " },
            { src: "assets/images/take_me_dancing/img_016.jpg", prompt: "See the colour in her eyes" },
            { src: "assets/images/take_me_dancing/img_017.jpg", prompt: "Then you'll take her palm and " },
            { src: "assets/images/take_me_dancing/img_018.jpg", prompt: "Lying, smoking on the ground" },
            { src: "assets/images/take_me_dancing/img_019.jpg", prompt: "And as I fall into the bottle " },
            { src: "assets/images/take_me_dancing/img_020.jpg", prompt: "You can make me into anything" },
            { src: "assets/images/take_me_dancing/img_021.jpg", prompt: "As long and I'm reflecting you" },
            { src: "assets/images/take_me_dancing/img_022.jpg", prompt: "Lonely is your love" },
            { src: "assets/images/take_me_dancing/img_023.jpg", prompt: "I could be the answer to" },
            { src: "assets/images/take_me_dancing/img_024.jpg", prompt: "All of your prayers" },
            { src: "assets/images/take_me_dancing/img_025.jpg", prompt: "Take me dancing" },
            { src: "assets/images/take_me_dancing/img_026.jpg", prompt: "Lonely ain't enough" },
            { src: "assets/images/take_me_dancing/img_027.jpg", prompt: "I could be the answer to" },
            { src: "assets/images/take_me_dancing/img_028.jpg", prompt: "All of your prayers" },
            { src: "assets/images/take_me_dancing/img_029.jpg", prompt: "Take me dancing" },
            { src: "assets/images/take_me_dancing/img_030.jpg", prompt: "Every moment (every moment)" },
            { src: "assets/images/take_me_dancing/img_031.jpg", prompt: "Always like this (always like " },
            { src: "assets/images/take_me_dancing/img_032.jpg", prompt: "We've got our come ups" },
            { src: "assets/images/take_me_dancing/img_033.jpg", prompt: "(We've got our come ups)" },
            { src: "assets/images/take_me_dancing/img_034.jpg", prompt: "And your dirty mind" },
            { src: "assets/images/take_me_dancing/img_035.jpg", prompt: "Lonely is your love" },
            { src: "assets/images/take_me_dancing/img_036.jpg", prompt: "I could be the answer to" },
            { src: "assets/images/take_me_dancing/img_037.jpg", prompt: "All of your prayers" },
            { src: "assets/images/take_me_dancing/img_038.jpg", prompt: "Take me dancing" },
            { src: "assets/images/take_me_dancing/img_039.jpg", prompt: "Lonely ain't enough" },
            { src: "assets/images/take_me_dancing/img_040.jpg", prompt: "I could be the answer to" },
            { src: "assets/images/take_me_dancing/img_041.jpg", prompt: "All of your prayers" },
            { src: "assets/images/take_me_dancing/img_042.jpg", prompt: "Take me dancing" },
            { src: "assets/images/take_me_dancing/img_043.jpg", prompt: "We could walk to the shitty ba" },
            { src: "assets/images/take_me_dancing/img_044.jpg", prompt: "We could swing to Americana" },
            { src: "assets/images/take_me_dancing/img_045.jpg", prompt: "I don't have much, don't make " },
            { src: "assets/images/take_me_dancing/img_046.jpg", prompt: "Take me dancing" },
            { src: "assets/images/take_me_dancing/img_047.jpg", prompt: "We could walk to the shitty ba" },
            { src: "assets/images/take_me_dancing/img_048.jpg", prompt: "We could swing to Americana" },
            { src: "assets/images/take_me_dancing/img_049.jpg", prompt: "I don't have much, don't make " },
            { src: "assets/images/take_me_dancing/img_050.jpg", prompt: "Take me dancing" }
        ],
        videoSrc: "assets/videos/take_me_dancing.mp4?v=20"
    },
    jane: {
        metadata: {"artist": "The Long Faces", "title": "Jane!", "album": "Jane!", "year": 2023},
        lyrics: `[00:01.49] Won't the devil guide your hand for good luck
[00:05.92] To hold the honeysuckle rose as she lies down
[00:12.74] Reading the paper, reading the world right round
[00:16.96] And her eyes record the sweet surprise of those who died that day
[00:25.87] Leaving her breathless, leading her hand to the grave
[00:41.87] And Jane, you're early
[00:45.35] Your life's work is dirtied by the fools who adore you
[00:52.16] Only to find, only to find you out
[00:56.66] They saw you dressing in the backroom
[01:00.96] Now they'll pay what they owe you
[01:05.13] It's only small change, red on the green green grass
[01:13.64] Won't the devil take you back for more
[01:18.25] To open closed doors and keep the good from the great
[01:25.06] Evil in equal, seeking to kill and create
[01:29.31] How grand
[01:31.41] The milk and honey land is on her tongue again
[01:38.20] Taste of the violence, trying to silence her head
[01:54.18] And Jane, you're early
[01:57.64] Your life's work is dirtied by the fools who adore you
[02:04.47] Biding your time, biding your time to strike, surely
[02:10.82] The poison makes a portrait of your face in the mirror
[02:17.59] Smiling with fright
[02:20.90] Ah!
[02:33.67] And Jane, you're early
[02:37.15] Your life's work is dirtied by the fools who adore you
[02:43.91] Only to find, only to find you out
[02:48.42] They saw you dressing in the backroom
[02:52.79] Now they'll pay what they owe you
[02:56.88] It's only small change, red on the green green grass`,
        images: [
            { src: "assets/images/jane/img_000.jpg", prompt: "Won't the devil guide your han" },
            { src: "assets/images/jane/img_001.jpg", prompt: "To hold the honeysuckle rose a" },
            { src: "assets/images/jane/img_002.jpg", prompt: "Reading the paper, reading the" },
            { src: "assets/images/jane/img_003.jpg", prompt: "And her eyes record the sweet " },
            { src: "assets/images/jane/img_004.jpg", prompt: "Leaving her breathless, leadin" },
            { src: "assets/images/jane/img_005.jpg", prompt: "And Jane, you're early" },
            { src: "assets/images/jane/img_006.jpg", prompt: "Your life's work is dirtied by" },
            { src: "assets/images/jane/img_007.jpg", prompt: "Only to find, only to find you" },
            { src: "assets/images/jane/img_008.jpg", prompt: "They saw you dressing in the b" },
            { src: "assets/images/jane/img_009.jpg", prompt: "Now they'll pay what they owe " },
            { src: "assets/images/jane/img_010.jpg", prompt: "It's only small change, red on" },
            { src: "assets/images/jane/img_011.jpg", prompt: "Won't the devil take you back " },
            { src: "assets/images/jane/img_012.jpg", prompt: "To open closed doors and keep " },
            { src: "assets/images/jane/img_013.jpg", prompt: "Evil in equal, seeking to kill" },
            { src: "assets/images/jane/img_014.jpg", prompt: "How grand" },
            { src: "assets/images/jane/img_015.jpg", prompt: "The milk and honey land is on " },
            { src: "assets/images/jane/img_016.jpg", prompt: "Taste of the violence, trying " },
            { src: "assets/images/jane/img_017.jpg", prompt: "And Jane, you're early" },
            { src: "assets/images/jane/img_018.jpg", prompt: "Your life's work is dirtied by" },
            { src: "assets/images/jane/img_019.jpg", prompt: "Biding your time, biding your " },
            { src: "assets/images/jane/img_020.jpg", prompt: "The poison makes a portrait of" },
            { src: "assets/images/jane/img_021.jpg", prompt: "Smiling with fright" },
            { src: "assets/images/jane/img_022.jpg", prompt: "Ah!" },
            { src: "assets/images/jane/img_023.jpg", prompt: "And Jane, you're early" },
            { src: "assets/images/jane/img_024.jpg", prompt: "Your life's work is dirtied by" },
            { src: "assets/images/jane/img_025.jpg", prompt: "Only to find, only to find you" },
            { src: "assets/images/jane/img_026.jpg", prompt: "They saw you dressing in the b" },
            { src: "assets/images/jane/img_027.jpg", prompt: "Now they'll pay what they owe " },
            { src: "assets/images/jane/img_028.jpg", prompt: "It's only small change, red on" }
        ],
        videoSrc: "assets/videos/jane.mp4?v=20"
    },
    kalapastangan: {
        metadata: {"artist": "fitterkarma", "title": "Kalapastangan", "album": "Kalapastangan", "year": 2023},
        lyrics: `[00:05.16] Oras nang sambahin ang ngalan Mo
[00:14.99] 
[00:17.00] Para mabuhay habang-buhay sa puso't isipan Mo
[00:26.97] 
[00:31.50] Sino ba ako para mapansin Mo?
[00:42.50] Mga dalangin ko sa 'Yo, sana'y pakinggan Mo
[00:49.11] 
[01:04.71] Pa'no ba ako magiging 'sang santo
[01:12.96] 
[01:16.38] Para makasama Kita diyan sa tabi ng trono Mo?
[01:24.73] 
[01:28.50] Ilan pang pagsubok ang daraanan ko
[01:36.53] 
[01:40.05] Bago ako makaranas ng mga milagro Mo?
[01:48.41] 
[02:09.95] Oh, ang langit ay nandito lamang pala sa lupa
[02:18.15] At ang impiyerno ay nasa isipan ko, at pinalimot ng 'Yong ganda
[02:27.87] Umaawit ang mga anghel, umaawit ang mga anghel
[02:37.17] Nagdiriwang sila nang makasama Kita, huwag Ka sanang mawawala
[02:45.64] Oh, oh, oh, oh
[02:52.07] Oh, ooh
[03:03.27] Mamamatay akong nakangiti
[03:07.58] Kapag Ikaw ang nasa aking tabi
[03:11.93] Mabubuhay akong nagsisisi
[03:16.33] Kapag 'sang araw hindi Kita mapangiti
[03:20.78] Kalapastangan ang 'di Ka ibigin
[03:25.36] Kalokohan ang 'di Ka isipin
[03:29.72] Kung ang mundo ay biglang gugunawin
[03:34.17] Ikaw ang una kong hahanapin
[03:39.02] Ooh
[03:45.63] 
[03:48.76] Ooh
[03:52.50] `,
        images: [
            { src: "assets/images/kalapastangan/img_000.jpg", prompt: "Oras nang sambahin ang ngalan Mo" },
            { src: "assets/images/kalapastangan/img_001.jpg", prompt: "[Instrumental Interlude]" },
            { src: "assets/images/kalapastangan/img_002.jpg", prompt: "Para mabuhay habang-buhay sa puso't isipan Mo" },
            { src: "assets/images/kalapastangan/img_003.jpg", prompt: "[Instrumental Interlude]" },
            { src: "assets/images/kalapastangan/img_004.jpg", prompt: "Sino ba ako para mapansin Mo?" },
            { src: "assets/images/kalapastangan/img_005.jpg", prompt: "Mga dalangin ko sa 'Yo, sana'y pakinggan Mo" },
            { src: "assets/images/kalapastangan/img_006.jpg", prompt: "[Instrumental Guitar Solo]" },
            { src: "assets/images/kalapastangan/img_007.jpg", prompt: "Pa'no ba ako magiging 'sang santo" },
            { src: "assets/images/kalapastangan/img_008.jpg", prompt: "[Instrumental Break]" },
            { src: "assets/images/kalapastangan/img_009.jpg", prompt: "Para makasama Kita diyan sa tabi ng trono Mo?" },
            { src: "assets/images/kalapastangan/img_010.jpg", prompt: "[Instrumental Break]" },
            { src: "assets/images/kalapastangan/img_011.jpg", prompt: "Ilan pang pagsubok ang daraanan ko" },
            { src: "assets/images/kalapastangan/img_012.jpg", prompt: "[Instrumental Interlude]" },
            { src: "assets/images/kalapastangan/img_013.jpg", prompt: "Bago ako makaranas ng mga milagro Mo?" },
            { src: "assets/images/kalapastangan/img_014.jpg", prompt: "[Instrumental Guitar Solo]" },
            { src: "assets/images/kalapastangan/img_015.jpg", prompt: "Oh, ang langit ay nandito lamang pala sa lupa" },
            { src: "assets/images/kalapastangan/img_016.jpg", prompt: "At ang impiyerno ay nasa isipan ko, at pinalimot ng 'Yong ganda" },
            { src: "assets/images/kalapastangan/img_017.jpg", prompt: "Umaawit ang mga anghel, umaawit ang mga anghel" },
            { src: "assets/images/kalapastangan/img_018.jpg", prompt: "Nagdiriwang sila nang makasama Kita, huwag Ka sanang mawawala" },
            { src: "assets/images/kalapastangan/img_019.jpg", prompt: "Oh, oh, oh, oh" },
            { src: "assets/images/kalapastangan/img_020.jpg", prompt: "Oh, ooh" },
            { src: "assets/images/kalapastangan/img_021.jpg", prompt: "Mamamatay akong nakangiti" },
            { src: "assets/images/kalapastangan/img_022.jpg", prompt: "Kapag Ikaw ang nasa aking tabi" },
            { src: "assets/images/kalapastangan/img_023.jpg", prompt: "Mabubuhay akong nagsisisi" },
            { src: "assets/images/kalapastangan/img_024.jpg", prompt: "Kapag 'sang araw hindi Kita mapangiti" },
            { src: "assets/images/kalapastangan/img_025.jpg", prompt: "Kalapastangan ang 'di Ka ibigin" },
            { src: "assets/images/kalapastangan/img_026.jpg", prompt: "Kalokohan ang 'di Ka isipin" },
            { src: "assets/images/kalapastangan/img_027.jpg", prompt: "Kung ang mundo ay biglang gugunawin" },
            { src: "assets/images/kalapastangan/img_028.jpg", prompt: "Ikaw ang una kong hahanapin" },
            { src: "assets/images/kalapastangan/img_029.jpg", prompt: "Ooh" },
            { src: "assets/images/kalapastangan/img_030.jpg", prompt: "[Instrumental Solo]" },
            { src: "assets/images/kalapastangan/img_031.jpg", prompt: "Ooh" },
            { src: "assets/images/kalapastangan/img_032.jpg", prompt: "[Instrumental Outro]" }
        ],
        videoSrc: "assets/videos/kalapastangan.mp4?v=20"
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

