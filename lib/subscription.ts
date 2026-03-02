import { prisma } from './prisma';

// 免费版限制
export const FREE_TIER_LIMITS = {
  dailyDigests: 3,
  channels: 10,
  summaryLength: 'short',
  historyDays: 7,
};

// 付费版权益
export const PAID_TIER_BENEFITS = {
  dailyDigests: Infinity,
  channels: 50,
  summaryLength: 'full',
  historyDays: Infinity,
  deepAnalysis: true,
  customKeywords: true,
};

export async function checkSubscription(userId: string) {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    include: {
      subscriptions: {
        where: {
          status: 'ACTIVE',
          endDate: { gt: new Date() },
        },
        orderBy: { endDate: 'desc' },
        take: 1,
      },
    },
  });

  if (!user) {
    return { access: false, reason: 'USER_NOT_FOUND' };
  }

  const activeSubscription = user.subscriptions[0];

  if (user.subscriptionStatus === 'FREE' || !activeSubscription) {
    return {
      access: true,
      plan: 'FREE',
      limits: FREE_TIER_LIMITS,
    };
  }

  return {
    access: true,
    plan: activeSubscription.plan,
    limits: PAID_TIER_BENEFITS,
    subscriptionEnd: activeSubscription.endDate,
  };
}

export function canAccessFeature(userTier: string, feature: string): boolean {
  if (userTier === 'FREE') {
    return ['basic_digest', 'limited_channels'].includes(feature);
  }
  return true;
}
