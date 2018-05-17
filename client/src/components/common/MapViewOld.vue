<template>
  <div class="map-view">
    <svg
      :width="`${width}px`"
      :height="`${height}px`"
      :viewBox="`0 0 ${width} ${height}`"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns="http://www.w3.org/2000/svg">
      <g class="region">
        <path
          v-for="datum in geometries"
          :key="datum.properties.name"
          :name="datum.properties.name"
          :style="style(datum)"
          :d="projection(datum)"/>
        <path
          v-for="(pair, idx) in pairs"
          :key="idx"
          :d="connect(pair)"
          :style="edgeStyle(pair)"/>
      </g>
    </svg>
  </div>
</template>

<script>
import { feature } from 'topojson-client';
import { geoConicConformal, geoPath } from 'd3-geo';

import map from '../../../static/russia_topo2.json';

export default {
  name: 'MapView',
  data() {
    return {
      geometries: feature(map, map.objects.name).features,
      width: 800,
      height: 600,
      projection: null,
      pairs: [
        ['BY', 'RU-MOS', [0.95, 0.55, 1.05, 0.65], false],
        ['BY', 'AM', [0.85, 1.15, 0.8, 1], true],
        ['BY', 'KZ', [1.1, 0.9, 1.05, 0.65], true],
        ['BY', 'KG', [1.55, 0.85, 1.05, 0.45], true],
        ['AM', 'RU-STA', [1.25, 1.05, 1.05, 1.05], false],
        ['AM', 'KZ', [0.95, 0.55, 1.05, 0.65], true],
        ['AM', 'KG', [0.95, 0.55, 1.05, 0.65], true],
        ['KZ', 'RU-SVE', [1.25, 1.05, 1.15, 1.1], false],
        ['KZ', 'KG', [0.95, 1.05, 0.85, 1.05], false],
        ['KG', 'RU-SVE', [1.25, 0.75, 1.25, 0.9], true],
      ],
    };
  },
  created() {
    this.projection = geoPath(geoConicConformal()
      .rotate([-95, -10])
      .center([-6, 65])
      // .parallels([53, 65])
      .scale(900)
      .translate([700, 0]));
  },
  methods: {
    edgeStyle([,,, isMgp]) {
      let color;
      if (isMgp) {
        color = 'blueviolet';
      } else {
        color = 'goldenrod';
      }
      return {
        fill: 'none', stroke: color, 'stroke-width': '2px',
      };
    },
    connect([_from, _to, [p1x, p1y, p2x, p2y]]) {
      const from = this.geometries.find(({ properties }) => properties.region === _from);
      const to = this.geometries.find(d => d.properties.region === _to);
      const [xfrom, yfrom] = this.projection.centroid(from);
      const [xto, yto] = this.projection.centroid(to);
      return `M${xfrom},${yfrom}C${xfrom * p1x} ${yfrom * p1y},${xto * p2x} ${yto * p2y},${xto} ${yto}`;
    },
    style({ properties }) {
      if (properties.isRussia) {
        return {
          fill: 'indianred',
          stroke: 'indianred',
        };
      }
      switch (properties.region) {
        case 'KZ':
          return {
            fill: '#00afca',
          };
        case 'KG':
          return {
            fill: '#e8112d',
          };
        case 'BY':
          return {
            fill: '#4aa657',
          };
        case 'AM':
          return {
            fill: '#D90012',
          };
        default:
          return {
            fill: '#eaeaea', stroke: '#bababa',
          };
      }
    },
  },
};
</script>

<style scoped>

  .map-view svg {
    background: url(https://scientificbsides.files.wordpress.com/2011/11/mapbig-cropped.jpg?w=1000);
    border-radius: 5px;
    border: 1px solid slategray;
  }

</style>
