<template>
  <div
    :class="{ 'session-item_open': session.status === 'open' }"
    class="session-item">
    <div class="session-item__main">
      <span class="session-item__session_type">{{ sessionType }}</span>
      <br>
      <span>{{ openDate }}</span>
    </div>
    <div class="session-item__target-date">
      <span>{{ targetDate }}</span>
    </div>
    <div style="min-width: 50px; display: flex; justify-content: center;">
      <span>{{ sessionNum }}</span>
    </div>
    <div style="min-width: 100px; display: flex; justify-content: center;">
      <span>{{ session.status === 'open' ? 'открыта' : 'завершена' }}</span>
    </div>
  </div>
</template>

<script>
import { format } from 'date-fns';

export default {
  name: 'SessionItem',
  props: {
    session: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      dateFmt: 'YYYY.MM.DD',
    };
  },
  computed: {
    sessionNum() {
      return `#${this.session._id}`;
    },
    sessionType() {
      switch (this.session.type) {
        case 'free':
          return 'СД';
        case 'futures':
          return 'Срочные контракты';
        case 'spot':
          return 'РСВ';
        default:
          throw new Error('ошибочный тип сессии!');
      }
    },
    openDate() {
      return format(this.session.openDate, 'YYYY.MM.DD HH:mm:ss');
    },
    targetDate() {
      if (this.session.type === 'spot') {
        return format(this.session.startDate, this.dateFmt);
      }
      return `${format(this.session.startDate, this.dateFmt)} – ${format(this.session.finishDate, this.dateFmt)}`;
    },
  },
};
</script>

<style>
  .session-item {
    display: flex;
    justify-content: space-around;
    background: rgb(255,255,255);
    border: 1px solid rgb(221,234,255);
    padding: 5px;
    margin: 2px;
    align-items: center;
    color: rgba(33, 33, 33, 0.54);
    font-size: 16px;
  }

  .session-item__main {
    width: 200px;
  }

  .session-item__session_type {
    color: black;
    font-size: 18px;
  }

  .session-item_open {
    background: rgb(223,237,214);
  }

  .session-item__target-date {
    width: 250px;
    display: flex;
    justify-content: space-around;
  }
</style>
