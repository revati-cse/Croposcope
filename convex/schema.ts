import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Users table for storing user profiles
  users: defineTable({
    userId: v.string(), // Auth user ID
    name: v.string(),
    email: v.string(),
    avatar: v.optional(v.string()),
    preferences: v.object({
      language: v.string(),
      notifications: v.boolean(),
      theme: v.string(),
    }),
  }).index("by_user_id", ["userId"]),

  // Crop analyses table for storing disease detection results
  analyses: defineTable({
    userId: v.string(),
    imageId: v.id("_storage"), // Reference to stored image
    crop: v.string(),
    disease: v.string(),
    confidence: v.number(),
    severity: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    fieldLocation: v.string(),
    treatmentApplied: v.boolean(),
    notes: v.optional(v.string()),
    metadata: v.object({
      modelVersion: v.string(),
      processingTime: v.number(),
      imageSize: v.object({
        width: v.number(),
        height: v.number(),
      }),
    }),
  }).index("by_user_id", ["userId"])
    .index("by_crop", ["crop"])
    .index("by_disease", ["disease"])
    .index("by_severity", ["severity"]),

  // Treatments table for organic treatment recommendations
  treatments: defineTable({
    name: v.string(),
    disease: v.string(),
    crop: v.string(),
    type: v.union(
      v.literal("organic"),
      v.literal("biological"), 
      v.literal("cultural"),
      v.literal("preventive")
    ),
    effectiveness: v.number(),
    duration: v.string(),
    difficulty: v.union(v.literal("easy"), v.literal("medium"), v.literal("hard")),
    ingredients: v.array(v.string()),
    instructions: v.array(v.string()),
    benefits: v.array(v.string()),
    precautions: v.array(v.string()),
    cost: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    season: v.array(v.string()),
  }).index("by_disease", ["disease"])
    .index("by_crop", ["crop"])
    .index("by_type", ["type"]),

  // Voice interactions table for accessibility features
  voiceInteractions: defineTable({
    userId: v.string(),
    transcript: v.string(),
    language: v.string(),
    command: v.optional(v.string()),
    response: v.optional(v.string()),
    timestamp: v.number(),
  }).index("by_user_id", ["userId"]),

  // Fields table for managing farm/field information
  fields: defineTable({
    userId: v.string(),
    name: v.string(),
    location: v.string(),
    size: v.number(), // in acres/hectares
    soilType: v.string(),
    cropHistory: v.array(v.object({
      year: v.number(),
      crop: v.string(),
      yield: v.optional(v.number()),
    })),
    currentCrop: v.optional(v.string()),
    notes: v.optional(v.string()),
  }).index("by_user_id", ["userId"]),

  // Disease library for comprehensive disease information
  diseases: defineTable({
    name: v.string(),
    scientificName: v.optional(v.string()),
    type: v.union(v.literal("fungal"), v.literal("bacterial"), v.literal("viral"), v.literal("pest")),
    affectedCrops: v.array(v.string()),
    symptoms: v.array(v.string()),
    causes: v.array(v.string()),
    organicTreatments: v.array(v.string()),
    prevention: v.array(v.string()),
    images: v.array(v.id("_storage")),
    severity: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    prevalence: v.string(), // seasonal information
  }).index("by_name", ["name"])
    .index("by_type", ["type"]),
});