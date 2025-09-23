import { ref } from 'vue'
import { defineStore } from 'pinia'
// 编写 Python 代码时不知道麻将的名字该这么写，以后重写的时候可能会改为正确的名字。

interface TileMap {
  [key: string]: string
}
interface ActionsType {
  hu: boolean | string // tile
  kong: boolean | string // tile
  pong: boolean | string // tile
  chow: [tile: string]
}

export const tilesmapStore = defineStore('tilemap', () => {
  const tilesmap = ref<TileMap>({
    '1t': 'Sou1',
    '2t': 'Sou2',
    '3t': 'Sou3',
    '4t': 'Sou4',
    '5t': 'Sou5',
    '6t': 'Sou6',
    '7t': 'Sou7',
    '8t': 'Sou8',
    '9t': 'Sou9',

    '1o': 'Pin1',
    '2o': 'Pin2',
    '3o': 'Pin3',
    '4o': 'Pin4',
    '5o': 'Pin5',
    '6o': 'Pin6',
    '7o': 'Pin7',
    '8o': 'Pin8',
    '9o': 'Pin9',

    '1w': 'Man1',
    '2w': 'Man2',
    '3w': 'Man3',
    '4w': 'Man4',
    '5w': 'Man5',
    '6w': 'Man6',
    '7w': 'Man7',
    '8w': 'Man8',
    '9w': 'Man9',

    e: 'Ton',
    s: 'Nan',
    w: 'Shaa',
    n: 'Pei',
    z: 'Chun',
    f: 'Hatsu',
    b: 'Haku',
    joker: 'Joker',
    back: 'Back',
  })
  const fontsmap = ref<TileMap>({
    '1o': '🀙',
    '2o': '🀚',
    '3o': '🀛',
    '4o': '🀜',
    '5o': '🀝',
    '6o': '🀞',
    '7o': '🀟',
    '8o': '🀠',
    '9o': '🀡',
    '1t': '🀐',
    '2t': '🀑',
    '3t': '🀒',
    '4t': '🀓',
    '5t': '🀔',
    '6t': '🀕',
    '7t': '🀖',
    '8t': '🀗',
    '9t': '🀘',
    '1w': '🀇',
    '2w': '🀈',
    '3w': '🀉',
    '4w': '🀊',
    '5w': '🀋',
    '6w': '🀌',
    '7w': '🀍',
    '8w': '🀎',
    '9w': '🀏',
    e: '🀀',
    s: '🀁',
    w: '🀂',
    n: '🀃',
    b: '🀆',
    f: '🀅',
    z: '🀄',
    joker: '🃏',
    back: '🀫',
    spring: '🀦',
    summer: '🀧',
    autumn: '🀨',
    winter: '🀩',
    plum: '🀢',
    orchid: '🀣',
    bamboo: '🀤',
    chrysanthemum: '🀥',
  })
  function getTileName(tile: string): string {
    if (tile) {
      return tilesmap.value[tile] || 'Blank'
    } else return ''
  }
  function getTilesName(tiles: string[]): string[] {
    if (tiles) {
      return tiles.map((tile) => getTileName(tile))
    } else return []
  }
  function getTileFont(tile: string | boolean): string {
    if (typeof tile === 'string') {
      return fontsmap.value[tile] || '�' // new tile may be ''
    } else return ''
  }
  function getTilesFont(tiles: string[]): string[] {
    if (tiles) {
      return tiles.map((tile) => getTileFont(tile))
    } else return []
  }
  function getActionsName(actions: ActionsType) {
    // {
    //   hu: true
    //   kong: true
    //   pong: true
    //   chow: [['1t','3t'], ['3t','4t']]
    // }
    const actionsname = []
    if (actions) {
      if (actions.hu) {
        actionsname.push(`胡${getTileFont(actions.hu)}`)
      }
      if (actions.kong) {
        actionsname.push(`杠${getTileFont(actions.kong)}`)
      }
      if (actions.pong) {
        actionsname.push(`碰${getTileFont(actions.pong)}`)
      }
      if (actions.chow) {
        for (const choice of actions.chow) {
          actionsname.push(`吃${getTileFont(choice[0])}${getTileFont(choice[1])}`) // choice is [tile,tile
        }
      }
    } else {
      return []
    }
    return actionsname
  }
  function getActionData(actions: ActionsType) {
    const actionsdata = []
    if (actions.hu) {
      actionsdata.push(true)
    }
    if (actions.kong) {
      actionsdata.push(true)
    }
    if (actions.pong) {
      actionsdata.push(true)
    }
    if (actions.chow) {
      for (const choice of actions.chow) {
        actionsdata.push(choice)
      }
    }
    console.log('getActionData', actions, actionsdata)
    return actionsdata
  }

  return {
    tilesmap,
    getTileName,
    getTilesName,
    fontsmap,
    getTileFont,
    getTilesFont,
    getActionsName,
    getActionData,
  }
})
