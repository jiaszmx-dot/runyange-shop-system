Page({
  data: {
    stores: [],
    services: [],
    storeId: "",
    serviceId: ""
  },

  onLoad() {
    const app = getApp();
    wx.request({
      url: `${app.globalData.apiBase}/stores`,
      header: { Authorization: `Bearer ${wx.getStorageSync("token") || ""}` },
      success: (res) => {
        const stores = res.data || [];
        this.setData({ stores, storeId: stores[0]?.id || "" });
      }
    });
    wx.request({
      url: `${app.globalData.apiBase}/services`,
      header: { Authorization: `Bearer ${wx.getStorageSync("token") || ""}` },
      success: (res) => {
        const services = res.data || [];
        this.setData({ services, serviceId: services[0]?.id || "" });
      }
    });
  },

  bindStore(e) {
    this.setData({ storeId: this.data.stores[e.detail.value].id });
  },

  bindService(e) {
    this.setData({ serviceId: this.data.services[e.detail.value].id });
  },

  submitBooking() {
    const app = getApp();
    wx.request({
      url: `${app.globalData.apiBase}/bookings`,
      method: "POST",
      header: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${wx.getStorageSync("token") || ""}`
      },
      data: {
        member_id: app.globalData.memberId,
        store_id: Number(this.data.storeId),
        service_id: Number(this.data.serviceId),
        booking_time: new Date().toISOString(),
        notes: "小程序预约"
      },
      success: () => wx.showToast({ title: "预约成功", icon: "success" }),
      fail: () => wx.showToast({ title: "预约失败", icon: "error" })
    });
  }
});
