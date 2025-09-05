import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { ConvexError } from "convex/values";

export const getOrCreateUser = mutation({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new ConvexError({
        message: "User not authenticated",
        code: "UNAUTHENTICATED",
      });
    }

    // Check if user already exists
    const existingUser = await ctx.db
      .query("users")
      .withIndex("by_user_id", (q) => q.eq("userId", identity.tokenIdentifier))
      .unique();

    if (existingUser) {
      return existingUser;
    }

    // Create new user
    const userId = await ctx.db.insert("users", {
      userId: identity.tokenIdentifier,
      name: identity.name ?? "Unknown User",
      email: identity.email ?? "",
      avatar: identity.pictureUrl,
      preferences: {
        language: "en",
        notifications: true,
        theme: "system",
      },
    });

    return await ctx.db.get(userId);
  },
});

export const getCurrentUser = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return null;
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_user_id", (q) => q.eq("userId", identity.tokenIdentifier))
      .unique();

    return user;
  },
});

export const updateUserPreferences = mutation({
  args: {
    language: v.optional(v.string()),
    notifications: v.optional(v.boolean()),
    theme: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new ConvexError({
        message: "User not authenticated",
        code: "UNAUTHENTICATED",
      });
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_user_id", (q) => q.eq("userId", identity.tokenIdentifier))
      .unique();

    if (!user) {
      throw new ConvexError({
        message: "User not found",
        code: "NOT_FOUND",
      });
    }

    await ctx.db.patch(user._id, {
      preferences: {
        ...user.preferences,
        ...(args.language !== undefined && { language: args.language }),
        ...(args.notifications !== undefined && { notifications: args.notifications }),
        ...(args.theme !== undefined && { theme: args.theme }),
      },
    });

    return await ctx.db.get(user._id);
  },
});