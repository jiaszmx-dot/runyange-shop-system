Page({
  data: {
    cards: [],
    referral: null
  },

  onLoad() {
    const app = getApp();
    wx.request({
      url: `${app.globalData.apiBase}/member-cards?member_id=${app.globalData.memberId}`,
      header: { Authorization: `Bearer ${wx.getStorageSync("token") || ""}` },
      success: (res) => this.setData({ cards: res.data || [] })
    });
    wx.request({
      url: `${app.globalData.apiBase}/referrals/${app.globalData.memberId}/progress`,
      header: { Authorization: `Bearer ${wx.getStorageSync("token") || ""}` },
      success: (res) => this.setData({ referral: res.data || null })
    });
  }
});
