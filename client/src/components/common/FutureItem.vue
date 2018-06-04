<template>
  <div class="future-item__wrapper">
    <div class="future-item__info future-item__info_head">
      <span>контракт</span>
      <span>#{{ future.deal_id }}</span>
    </div>
    <div class="future-item__info">
      <span>период</span>
      <span>{{ period }}</span>
    </div>
    <div class="future-item__info">
      <span>график поставки</span>
      <span>{{ graphType }}</span>
    </div>
    <div class="future-item__info">
      <span>поставщик</span>
      <span>{{ future.seller_code }}</span>
    </div>
    <div class="future-item__info">
      <span>покупатель</span>
      <span>{{ future.buyer_code }}</span>
    </div>
    <div class="future-item__info">
      <span>код сечения</span>
      <span>{{ future.section_code }}</span>
    </div>
    <div class="future-item__info">
      <span>объем лота</span>
      <span>{{ splitter(future.volume) }}</span>
    </div>
    <div class="future-item__info">
      <span>стоимость</span>
      <span>{{ splitter(future.sum_volume * future.price) }}</span>
    </div>
    <div
      v-if="rioEntry['dir'] === 'buy'"
      class="future-item__info">
      <span>стоимость МГП</span>
      <span>{{ future.mgp_price ? splitter(future.sum_volume * future.mgp_price) : 0 }}</span>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { format } from 'date-fns';

export default {
  name: 'FutureItem',
  props: {
    future: {
      type: Object,
      required: true,
    },
  },
  computed: {
    ...mapState('common', ['rioEntry']),
    period() {
      return `${format(this.future.start_date, 'YYYY.MM.DD')} - ${format(this.future.finish_date, 'YYYY.MM.DD')}`;
    },
    graphType() {
      if (this.future.graph_type === 'BL') {
        return 'базовый';
      }
      return 'пиковый';
    },
  },
  methods: {
    splitter(val) {
      if (val === undefined || val === null) return null;
      return val.toString().replace(/\B(?=(?:\d{3})+(?!\d))/g, ' ');
    },
  },
};
</script>

<style>
.future-item__wrapper {
  display: flex;
  justify-content: space-around;
  border: 1px solid cornflowerblue;
  margin: 5px;
  background: #eee;
}

.future-item__info {
  display: flex;
  flex-direction: column;
  padding: 10px 0;
}

.future-item__info:not(.future-item__info_head) {
  align-items: center;
}

.future-item__info span:last-child {
  color: grey;
}
</style>
