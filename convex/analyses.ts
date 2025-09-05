import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { ConvexError } from "convex/values";
import { paginationOptsValidator } from "convex/server";

export const createAnalysis = mutation({
  args: {
    imageId: v.id("_storage"),
    crop: v.string(),
    disease: v.string(),
    confidence: v.number(),
    severity: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    fieldLocation: v.string(),
    notes: v.optional(v.string()),
    modelVersion: v.string(),
    processingTime: v.number(),
    imageWidth: v.number(),
    imageHeight: v.number(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new ConvexError({
        message: "User not authenticated",
        code: "UNAUTHENTICATED",
      });
    }

    const analysisId = await ctx.db.insert("analyses", {
      userId: identity.tokenIdentifier,
      imageId: args.imageId,
      crop: args.crop,
      disease: args.disease,
      confidence: args.confidence,
      severity: args.severity,
      fieldLocation: args.fieldLocation,
      treatmentApplied: false,
      notes: args.notes,
      metadata: {
        modelVersion: args.modelVersion,
        processingTime: args.processingTime,
        imageSize: {
          width: args.imageWidth,
          height: args.imageHeight,
        },
      },
    });

    return await ctx.db.get(analysisId);
  },
});

export const getUserAnalyses = query({
  args: {
    paginationOpts: paginationOptsValidator,
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return { page: [], isDone: true, continueCursor: null };
    }

    const results = await ctx.db
      .query("analyses")
      .withIndex("by_user_id", (q) => q.eq("userId", identity.tokenIdentifier))
      .order("desc")
      .paginate(args.paginationOpts);

    return results;
  },
});

export const getAnalysisById = query({
  args: { id: v.id("analyses") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return null;
    }

    const analysis = await ctx.db.get(args.id);
    if (!analysis || analysis.userId !== identity.tokenIdentifier) {
      return null;
    }

    return analysis;
  },
});

export const updateTreatmentStatus = mutation({
  args: {
    analysisId: v.id("analyses"),
    treatmentApplied: v.boolean(),
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new ConvexError({
        message: "User not authenticated",
        code: "UNAUTHENTICATED",
      });
    }

    const analysis = await ctx.db.get(args.analysisId);
    if (!analysis || analysis.userId !== identity.tokenIdentifier) {
      throw new ConvexError({
        message: "Analysis not found or access denied",
        code: "NOT_FOUND",
      });
    }

    await ctx.db.patch(args.analysisId, {
      treatmentApplied: args.treatmentApplied,
      ...(args.notes && { notes: args.notes }),
    });

    return await ctx.db.get(args.analysisId);
  },
});

export const getAnalyticsData = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return null;
    }

    const analyses = await ctx.db
      .query("analyses")
      .withIndex("by_user_id", (q) => q.eq("userId", identity.tokenIdentifier))
      .collect();

    const totalAnalyses = analyses.length;
    const diseaseDetected = analyses.filter(a => a.disease !== "Healthy").length;
    const averageConfidence = totalAnalyses > 0 
      ? analyses.reduce((sum, a) => sum + a.confidence, 0) / totalAnalyses 
      : 0;
    const treatmentCompliance = totalAnalyses > 0 
      ? (analyses.filter(a => a.treatmentApplied).length / totalAnalyses) * 100 
      : 0;

    // Disease distribution
    const diseaseStats = analyses.reduce((acc, analysis) => {
      acc[analysis.disease] = (acc[analysis.disease] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Crop distribution
    const cropStats = analyses.reduce((acc, analysis) => {
      acc[analysis.crop] = (acc[analysis.crop] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Severity distribution
    const severityStats = analyses.reduce((acc, analysis) => {
      acc[analysis.severity] = (acc[analysis.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalAnalyses,
      diseaseDetected,
      averageConfidence,
      treatmentCompliance,
      diseaseStats,
      cropStats,
      severityStats,
    };
  },
});

export const deleteAnalysis = mutation({
  args: { id: v.id("analyses") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new ConvexError({
        message: "User not authenticated", 
        code: "UNAUTHENTICATED",
      });
    }

    const analysis = await ctx.db.get(args.id);
    if (!analysis || analysis.userId !== identity.tokenIdentifier) {
      throw new ConvexError({
        message: "Analysis not found or access denied",
        code: "NOT_FOUND",
      });
    }

    await ctx.db.delete(args.id);
    return { success: true };
  },
});