class Api {
  constructor(url) {
    this.url = url;
    this.ws = new WebSocket(this.url);
    ws.onopen = this.onOpen;
    ws.onclose = this.onClose;
    ws.onmessage = this.onMessage;
  }

  onOpen() {
    console.log(`web socket connection to ${this.url} established`);
  }

  onClose({ wasClean, reason }) {
    console.log(`web socket connection to ${this.url} closed due to ${reason}`);
  }

  onMessage(msg) {
    console.log(`Сообщение ${msg.data}`);
  }

  send(data) {
    this.ws.send(JSON.stringify(data));
  }
}

export default Api;
