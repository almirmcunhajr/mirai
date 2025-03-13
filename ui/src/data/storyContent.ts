import { StoryContent } from '../types';

export const storyContent: Record<string, StoryContent> = {
  fantasy: {
    initial: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', // 15 sec video
      decisions: [
        {
          text: "Follow the mysterious light",
          nextNode: "forest"
        },
        {
          text: "Stay in the village",
          nextNode: "village"
        }
      ]
    },
    forest: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', // 15 sec video
      decisions: [
        {
          text: "Use magic to communicate",
          nextNode: "magic"
        },
        {
          text: "Search for artifacts",
          nextNode: "search"
        }
      ]
    },
    magic: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4', // 15 sec video
      decisions: [
        {
          text: "Accept the spirit's offer",
          nextNode: "accept"
        },
        {
          text: "Decline and leave",
          nextNode: "decline"
        }
      ]
    },
    village: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4', // 15 sec video
      decisions: [
        {
          text: "Help defend the village",
          nextNode: "defend"
        },
        {
          text: "Seek the elder's wisdom",
          nextNode: "wisdom"
        }
      ]
    }
  },
  'sci-fi': {
    initial: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4', // 15 sec video
      decisions: [
        {
          text: "Investigate the signal",
          nextNode: "signal"
        },
        {
          text: "Prepare defenses",
          nextNode: "defense"
        }
      ]
    },
    signal: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4', // 15 sec video
      decisions: [
        {
          text: "Make contact",
          nextNode: "contact"
        },
        {
          text: "Return to base",
          nextNode: "return"
        }
      ]
    },
    defense: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4', // 15 sec video
      decisions: [
        {
          text: "Launch counter-attack",
          nextNode: "attack"
        },
        {
          text: "Negotiate peace",
          nextNode: "peace"
        }
      ]
    }
  },
  mystery: {
    initial: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4', // 15 sec video
      decisions: [
        {
          text: "Follow the suspect",
          nextNode: "chase"
        },
        {
          text: "Examine the evidence",
          nextNode: "evidence"
        }
      ]
    },
    chase: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4', // 15 sec video
      decisions: [
        {
          text: "Corner the suspect",
          nextNode: "corner"
        },
        {
          text: "Call for backup",
          nextNode: "backup"
        }
      ]
    },
    evidence: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4', // 15 sec video
      decisions: [
        {
          text: "Analyze at the lab",
          nextNode: "lab"
        },
        {
          text: "Search for more clues",
          nextNode: "search"
        }
      ]
    }
  },
  horror: {
    initial: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', // 15 sec video
      decisions: [
        {
          text: "Hide in the basement",
          nextNode: "basement"
        },
        {
          text: "Run to the car",
          nextNode: "car"
        }
      ]
    },
    basement: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', // 15 sec video
      decisions: [
        {
          text: "Search for weapons",
          nextNode: "weapons"
        },
        {
          text: "Stay quiet",
          nextNode: "quiet"
        }
      ]
    },
    car: {
      videoUrl: 'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4', // 15 sec video
      decisions: [
        {
          text: "Drive to the police",
          nextNode: "police"
        },
        {
          text: "Hide in the woods",
          nextNode: "woods"
        }
      ]
    }
  }
};