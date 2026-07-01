<template>
  <el-container class="app-shell">
    <!-- ===== 顶部导航栏 ===== -->
    <el-header class="app-header" height="56px">
      <div class="app-header__brand">
        <img src="@/assets/indicator.png" alt="logo" class="app-header__logo" />
        <span class="app-header__name">CDDP Workbench</span>
        <span class="app-header__divider" />
        <span class="app-header__subtitle">配置驱动开发平台-工作台</span>
      </div>
    </el-header>

    <!-- ===== 页面内容区 ===== -->
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style lang="less">
/* 让根节点和 body 撑满全屏 */
html, body, #app {
  height: 100%;
  margin: 0;
  overflow: hidden;
}

/* 外层容器：垂直排列，占满全屏 */
.app-shell {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* ── 顶部 Header ── */
.app-header {
  background: linear-gradient(135deg, #0077ff 0%, #0060e7 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex !important;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
  gap: 24px;
}

.app-header__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  padding-top: 4px;
}

.app-header__logo {
  width: 30px;
  height: 30px;
  object-fit: contain;
  margin-top: -4px;
}

.app-header__name {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.5px;
  white-space: nowrap;
  line-height: 1;
}

.app-header__divider {
  width: 1px;
  height: 16px;
  background: rgba(255, 255, 255, 0.35);
  flex-shrink: 0;
}

.app-header__subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
  line-height: 1;
}

/* ── 主内容区 ── */
.app-main {
  flex: 1 !important;
  height: 0;           /* 配合 flex:1 撑满剩余高度 */
  overflow-y: auto;
  background-color: #f5f7fa;
  padding: 0px !important;
}
</style>