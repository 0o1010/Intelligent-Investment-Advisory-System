<template>
    <div id="app" >
<!--        <Index></Index>-->
        <router-view></router-view>
<!--        <Login></Login>-->
    </div>
</template>

<script>

// import Login from "@/pages/Login";
// import Index from "@/components/Index";

export default {
    name: 'App',
    components: {
        // Index,
        // Login
    }
}
</script>
<style>

#app {
  height: 100%;
}
</style>
