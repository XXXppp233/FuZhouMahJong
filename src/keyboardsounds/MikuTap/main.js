import data from './main.json'

export default {
  Play(e) {
    //event
    const code = 65 <= e.keyCode ? e.keyCode - 55 : 48 <= e.keyCode ? e.keyCode - 48 : e.keyCode
    const audioCode = code % 32

    const audioName = `${audioCode}.mp3`
    const audio = new Audio(data[audioName])
    audio.play()
  },
}
