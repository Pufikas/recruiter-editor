<template>
    <canvas ref="canvas"></canvas>
</template>

<script setup>
import * as d3 from 'd3';
import { onMounted, ref, watch, defineProps } from 'vue';
import { getRecruiters } from '../db/database';
import { formattedHierarchical } from '@/lib/formatData';

const props = defineProps({
    width: {
        type: Number,
        default: 1900
    },

    height: {
        type: Number,
        default: 1300
    }
});

const data = ref([]);
const canvas = ref(null);
let root = null;
let ctx;
let transform = d3.zoomIdentity;

const zoom = d3.zoom()
    .scaleExtent([0.5, 5])
    .on('zoom', (event) => {
        transform = event.transform
        draw()
    });


const drawTree = () => {
    // root = d3.hierarchy(data.value[0]); // returns a single parent's tree (could use for personal tree)

    // no one is parent
    const virutalRoot = {
        name: 'root',
        children: data.value
    }
    root = d3.hierarchy(virutalRoot);

    // tree with founder as a root
    // const founder = data.value[0];
    // founder.children = [...(founder.children || []), ...data.value.slice(1)];
    // root = d3.hierarchy(founder);

    // d3.tree().size([props.width, props.height])(root); // this doesnt rly work with a lot of data
    
    // pretty sure this gives 1 to 1 tree based on v1
    d3.tree()
        .nodeSize([80, 140]) // horizontal, vertical spacing
        (root);
    
    draw();
    d3.select(canvas.value).call(zoom);
}

const draw = () => {
    ctx.save();
    ctx.clearRect(0, 0, props.width, props.height);
    ctx.translate(transform.x + props.width / 2, transform.y + 40);

    ctx.scale(transform.k, transform.k);

    // links
    root.links()
        // filter is needed only for virtual root
        .filter(l => l.source.depth > 0)
        .forEach(link => {
            ctx.beginPath()
            ctx.moveTo(link.source.x, link.source.y)
            ctx.lineTo(link.target.x, link.target.y)
            ctx.strokeStyle = "pink"
            ctx.stroke()
        });

    // nodes
    root.descendants()
        .slice(1) // ignore root node
        .forEach(d => {
            ctx.beginPath()
            ctx.arc(d.x, d.y, 5, 0, Math.PI * 2)
            ctx.fillStyle = "white"
            ctx.fill()
            ctx.fillText(d.data.name, d.x, d.y - 10)
        });

    ctx.restore();
}

onMounted(async () => {
    data.value = await formattedHierarchical(false);

    ctx = canvas.value.getContext('2d');
    canvas.value.width = props.width;
    canvas.value.height = props.height;
    drawTree();
});

</script>


<style scoped>

</style>