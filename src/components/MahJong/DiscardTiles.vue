<template>
    <div>
        <b v-for="tile in props.discarded">{{ tile }}</b>
    </div>
</template>

<script setup>

const props = defineProps({
  discarded: {
    type: Array,
    default: () => []
  }
})

</script>

<style scoped>
div {
    caret-color: transparent; /* 隐藏光标 */
    margin: 1vh 0;  
    height: 6vh;
    width: 42vw;
    font-size: 3vh;
    font-family: 'Segoe UI Symbol';
    display: inline-block;
    word-break: break-word;
    line-height: 1;
    white-space: normal;
}

b:hover {
    cursor: pointer;
    color: green;
}
</style>
