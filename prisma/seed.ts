import {
  PrismaClient,
  PromotionCampaignType,
  RewardPayoutType,
  ServicePricingUnit,
  StoreOwnershipType,
  StoreStatus,
  UserRole,
  UserStatus,
} from "@prisma/client";

import {
  deductionRules,
  followUpRules,
  productRules,
  promotionRules,
  rechargePlanRules,
  roleRules,
  serviceRules,
} from "../src/lib/business-rules";

const prisma = new PrismaClient();

const organizationCode = "RUNYANGGE";
const storeCode = "HQ-001";
const storeName = "总店";

function uniqueBy<T>(items: T[], getKey: (item: T) => string): T[] {
  const map = new Map<string, T>();
  for (const item of items) {
    map.set(getKey(item), item);
  }
  return Array.from(map.values());
}

async function main() {
  const organization = await prisma.organization.upsert({
    where: { code: organizationCode },
    update: {
      name: "润阳阁",
      brandName: "润阳阁云店铺",
      status: StoreStatus.ACTIVE,
    },
    create: {
      code: organizationCode,
      name: "润阳阁",
      brandName: "润阳阁云店铺",
      status: StoreStatus.ACTIVE,
    },
  });

  const store = await prisma.store.upsert({
    where: {
      organizationId_code: {
        organizationId: organization.id,
        code: storeCode,
      },
    },
    update: {
      name: storeName,
      ownershipType: StoreOwnershipType.DIRECT,
      status: StoreStatus.ACTIVE,
      allowsPricingOverride: true,
      allowsPromotionOverride: true,
    },
    create: {
      organizationId: organization.id,
      code: storeCode,
      name: storeName,
      ownershipType: StoreOwnershipType.DIRECT,
      status: StoreStatus.ACTIVE,
      allowsPricingOverride: true,
      allowsPromotionOverride: true,
    },
  });

  const serviceCategoryMap = new Map<string, string>();
  const serviceCategories = uniqueBy(serviceRules, (rule) => rule.category).map((rule) => rule.category);
  for (const categoryName of serviceCategories) {
    const category = await prisma.serviceCategory.upsert({
      where: { id: `${organization.id}-${categoryName}` },
      update: { name: categoryName },
      create: {
        id: `${organization.id}-${categoryName}`,
        organizationId: organization.id,
        name: categoryName,
      },
    });
    serviceCategoryMap.set(categoryName, category.id);
  }

  const productCategoryMap = new Map<string, string>();
  const productCategories = uniqueBy(productRules, (rule) => rule.category).map((rule) => rule.category);
  for (const categoryName of productCategories) {
    const category = await prisma.productCategory.upsert({
      where: { id: `${organization.id}-${categoryName}` },
      update: { name: categoryName },
      create: {
        id: `${organization.id}-${categoryName}`,
        organizationId: organization.id,
        name: categoryName,
      },
    });
    productCategoryMap.set(categoryName, category.id);
  }

  const serviceItemIds = new Map<string, string>();
  for (const service of serviceRules) {
    const code = `${service.category}-${service.name}-${service.pricingUnit}`;
    const item = await prisma.serviceItem.upsert({
      where: { id: `${organization.id}-${code}` },
      update: {
        code,
        name: service.name,
        listPrice: service.listPrice,
        memberPrice: service.memberPrice,
        durationMinutes: service.durationMinutes,
        serviceCommission: service.commissionAmount,
        consumableCostNote: service.consumableNote ?? null,
        isEnabled: service.enabled,
        pricingUnit: service.pricingUnit === "小时" ? ServicePricingUnit.PER_HOUR : ServicePricingUnit.PER_VISIT,
      },
      create: {
        id: `${organization.id}-${code}`,
        categoryId: serviceCategoryMap.get(service.category)!,
        code,
        name: service.name,
        listPrice: service.listPrice,
        memberPrice: service.memberPrice,
        durationMinutes: service.durationMinutes,
        serviceCommission: service.commissionAmount,
        consumableCostNote: service.consumableNote ?? null,
        isEnabled: service.enabled,
        pricingUnit: service.pricingUnit === "小时" ? ServicePricingUnit.PER_HOUR : ServicePricingUnit.PER_VISIT,
      },
    });

    serviceItemIds.set(service.name, item.id);

    await prisma.storeServicePrice.upsert({
      where: {
        storeId_serviceItemId: {
          storeId: store.id,
          serviceItemId: item.id,
        },
      },
      update: {
        listPrice: service.listPrice,
        memberPrice: service.memberPrice,
        isEnabled: service.enabled,
      },
      create: {
        storeId: store.id,
        serviceItemId: item.id,
        listPrice: service.listPrice,
        memberPrice: service.memberPrice,
        isEnabled: service.enabled,
      },
    });
  }

  for (const rule of deductionRules) {
    const serviceItemId = serviceItemIds.get(rule.serviceName);
    if (!serviceItemId) {
      continue;
    }

    await prisma.serviceSettlementPolicy.upsert({
      where: { serviceItemId },
      update: {
        allowStoredValue: rule.allowStoredValue,
        allowGiftTimes: rule.allowGiftTimes,
        allowProjectVoucher: rule.allowProjectVoucher,
        allowPackage: rule.allowPackages,
        packageTemplateName: rule.packageName ?? null,
        note: rule.note ?? null,
      },
      create: {
        serviceItemId,
        allowStoredValue: rule.allowStoredValue,
        allowGiftTimes: rule.allowGiftTimes,
        allowProjectVoucher: rule.allowProjectVoucher,
        allowPackage: rule.allowPackages,
        packageTemplateName: rule.packageName ?? null,
        note: rule.note ?? null,
      },
    });
  }

  for (const product of productRules) {
    const code = `${product.category}-${product.name}`;
    const item = await prisma.product.upsert({
      where: { id: `${organization.id}-${code}` },
      update: {
        code,
        name: product.name,
        listPrice: product.listPrice,
        memberPrice: product.memberPrice,
        saleCommission: product.commissionAmount,
        tracksInventory: product.tracksInventory,
        isConsumable: product.type === "耗材",
      },
      create: {
        id: `${organization.id}-${code}`,
        categoryId: productCategoryMap.get(product.category)!,
        code,
        name: product.name,
        listPrice: product.listPrice,
        memberPrice: product.memberPrice,
        saleCommission: product.commissionAmount,
        tracksInventory: product.tracksInventory,
        isConsumable: product.type === "耗材",
      },
    });

    await prisma.storeProductPrice.upsert({
      where: {
        storeId_productId: {
          storeId: store.id,
          productId: item.id,
        },
      },
      update: {
        listPrice: product.listPrice,
        memberPrice: product.memberPrice,
      },
      create: {
        storeId: store.id,
        productId: item.id,
        listPrice: product.listPrice,
        memberPrice: product.memberPrice,
      },
    });

    await prisma.inventoryItem.upsert({
      where: {
        storeId_productId: {
          storeId: store.id,
          productId: item.id,
        },
      },
      update: {
        warningLevel: product.warningStock,
      },
      create: {
        storeId: store.id,
        productId: item.id,
        quantity: 0,
        warningLevel: product.warningStock,
        itemType: product.type === "耗材" ? "CONSUMABLE" : "PRODUCT",
      },
    });
  }

  for (const plan of rechargePlanRules) {
    const rechargePlan = await prisma.rechargePlan.upsert({
      where: { id: `${organization.id}-${plan.name}` },
      update: {
        name: plan.name,
        rechargeAmount: plan.rechargeAmount,
        rewardRate: plan.commissionRate,
        isEnabled: true,
      },
      create: {
        id: `${organization.id}-${plan.name}`,
        organizationId: organization.id,
        name: plan.name,
        rechargeAmount: plan.rechargeAmount,
        rewardRate: plan.commissionRate,
        isEnabled: true,
      },
    });

    const giftServiceId = serviceItemIds.get(plan.giftService);
    if (!giftServiceId) {
      continue;
    }

    await prisma.rechargePlanGift.upsert({
      where: { id: `${rechargePlan.id}-${plan.giftService}` },
      update: {
        quantity: plan.giftTimes,
      },
      create: {
        id: `${rechargePlan.id}-${plan.giftService}`,
        rechargePlanId: rechargePlan.id,
        serviceItemId: giftServiceId,
        quantity: plan.giftTimes,
      },
    });
  }

  for (const campaign of promotionRules) {
    const campaignId = `${organization.id}-${campaign.title}`;
    const promotion = await prisma.promotionCampaign.upsert({
      where: { id: campaignId },
      update: {
        title: campaign.title,
        campaignType:
          campaign.campaignType === "返现奖励"
            ? PromotionCampaignType.REFERRAL_CASHBACK
            : PromotionCampaignType.VOUCHER,
        description: `${campaign.benefit} / ${campaign.condition}`,
        isEnabled: true,
      },
      create: {
        id: campaignId,
        organizationId: organization.id,
        title: campaign.title,
        campaignType:
          campaign.campaignType === "返现奖励"
            ? PromotionCampaignType.REFERRAL_CASHBACK
            : PromotionCampaignType.VOUCHER,
        description: `${campaign.benefit} / ${campaign.condition}`,
        isEnabled: true,
      },
    });

    if (campaign.campaignType === "返现奖励") {
      await prisma.referralRewardRule.upsert({
        where: { campaignId: promotion.id },
        update: {
          triggerReferralCount: campaign.referralTargetCount ?? 0,
          qualifyingRechargeAmount: campaign.qualifyingRechargeAmount ?? null,
          rewardAmount: campaign.rewardAmount ?? 0,
          payoutType: RewardPayoutType.CASHBACK,
          note: campaign.fulfillmentMethod,
        },
        create: {
          campaignId: promotion.id,
          triggerReferralCount: campaign.referralTargetCount ?? 0,
          qualifyingRechargeAmount: campaign.qualifyingRechargeAmount ?? null,
          rewardAmount: campaign.rewardAmount ?? 0,
          payoutType: RewardPayoutType.CASHBACK,
          note: campaign.fulfillmentMethod,
        },
      });
    }
  }

  for (const profile of roleRules) {
    const user = await prisma.user.upsert({
      where: {
        phone: `seed-${profile.employeeName}`,
      },
      update: {
        fullName: profile.employeeName,
        status: UserStatus.ACTIVE,
      },
      create: {
        organizationId: organization.id,
        fullName: profile.employeeName,
        phone: `seed-${profile.employeeName}`,
        status: UserStatus.ACTIVE,
        passwordHash: "pending-auth-setup",
      },
    });

    const roleMap: Record<string, UserRole> = {
      总部管理员: UserRole.HQ_SUPER_ADMIN,
      总部运营: UserRole.HQ_OPERATOR,
      店长: UserRole.STORE_MANAGER,
      收银员: UserRole.CASHIER,
      员工: UserRole.THERAPIST,
    };

    await prisma.userAccess.upsert({
      where: {
        userId_storeId_role: {
          userId: user.id,
          storeId: store.id,
          role: roleMap[profile.role] ?? UserRole.THERAPIST,
        },
      },
      update: {
        canViewAllStores: profile.role.includes("总部"),
        canEditDirectStores: profile.role !== "员工",
        canEditFranchiseStores: profile.role === "总部管理员" || profile.role === "总部运营",
      },
      create: {
        userId: user.id,
        storeId: store.id,
        role: roleMap[profile.role] ?? UserRole.THERAPIST,
        canViewAllStores: profile.role.includes("总部"),
        canEditDirectStores: profile.role !== "员工",
        canEditFranchiseStores: profile.role === "总部管理员" || profile.role === "总部运营",
      },
    });
  }

  console.log(
    `Seed complete: ${rechargePlanRules.length} recharge plans, ${serviceRules.length} services, ${deductionRules.length} settlement policies, ${productRules.length} products, ${roleRules.length} users, ${promotionRules.length} campaigns. Parsed ${followUpRules.length} follow-up rules for later implementation.`,
  );
}

main()
  .catch((error) => {
    console.error(error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
