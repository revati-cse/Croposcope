import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const getTreatments = query({
  args: {
    disease: v.optional(v.string()),
    crop: v.optional(v.string()),
    type: v.optional(v.union(v.literal("organic"), v.literal("biological"), v.literal("cultural"), v.literal("preventive"))),
  },
  handler: async (ctx, args) => {
    let results;

    if (args.disease) {
      results = await ctx.db
        .query("treatments")
        .withIndex("by_disease", (q) => q.eq("disease", args.disease!))
        .collect();
    } else if (args.crop) {
      results = await ctx.db
        .query("treatments")
        .withIndex("by_crop", (q) => q.eq("crop", args.crop!))
        .collect();
    } else if (args.type) {
      results = await ctx.db
        .query("treatments")
        .withIndex("by_type", (q) => q.eq("type", args.type!))
        .collect();
    } else {
      results = await ctx.db.query("treatments").collect();
    }

    return results;
  },
});

export const searchTreatments = query({
  args: {
    searchQuery: v.string(),
  },
  handler: async (ctx, args) => {
    const allTreatments = await ctx.db.query("treatments").collect();
    
    const searchTerm = args.searchQuery.toLowerCase();
    return allTreatments.filter(treatment =>
      treatment.name.toLowerCase().includes(searchTerm) ||
      treatment.disease.toLowerCase().includes(searchTerm) ||
      treatment.crop.toLowerCase().includes(searchTerm) ||
      treatment.ingredients.some(ingredient => 
        ingredient.toLowerCase().includes(searchTerm)
      )
    );
  },
});

// Pre-populate with sample organic treatments
export const seedTreatments = mutation({
  args: {},
  handler: async (ctx) => {
    const treatments = [
      {
        name: "Neem Oil Spray",
        disease: "Aphids, Powdery Mildew, Leaf Spot",
        crop: "Tomato, Potato, Corn",
        type: "organic" as const,
        effectiveness: 85,
        duration: "7-14 days",
        difficulty: "easy" as const,
        ingredients: ["Neem oil (2-3 tbsp)", "Liquid soap (1 tsp)", "Water (1 liter)"],
        instructions: [
          "Mix neem oil and liquid soap in warm water",
          "Stir thoroughly until well combined",
          "Spray on affected areas in early morning or evening",
          "Reapply every 7-10 days or after rain"
        ],
        benefits: [
          "100% organic and safe for humans",
          "Effective against multiple pests and diseases",
          "Doesn't harm beneficial insects",
          "Biodegradable and eco-friendly"
        ],
        precautions: [
          "Don't spray in direct sunlight",
          "Test on small area first",
          "Avoid during flowering for pollinator safety"
        ],
        cost: "low" as const,
        season: ["Spring", "Summer", "Fall"]
      },
      {
        name: "Baking Soda Fungicide",
        disease: "Powdery Mildew, Black Spot, Rust",
        crop: "Tomato, Cucumber, Rose",
        type: "organic" as const,
        effectiveness: 78,
        duration: "5-7 days",
        difficulty: "easy" as const,
        ingredients: ["Baking soda (1 tbsp)", "Liquid soap (1/2 tsp)", "Water (1 liter)"],
        instructions: [
          "Dissolve baking soda in water",
          "Add liquid soap and mix gently",
          "Spray on both sides of leaves",
          "Apply weekly during humid conditions"
        ],
        benefits: [
          "Readily available household item",
          "Safe for edible crops", 
          "Changes leaf surface pH to prevent fungal growth",
          "Very cost-effective"
        ],
        precautions: [
          "Don't exceed recommended concentration",
          "May cause leaf burn if overused",
          "Best used as prevention"
        ],
        cost: "low" as const,
        season: ["Summer", "Fall"]
      },
      {
        name: "Companion Planting",
        disease: "Various Pests and Diseases",
        crop: "All crops",
        type: "cultural" as const,
        effectiveness: 70,
        duration: "Full growing season",
        difficulty: "medium" as const,
        ingredients: ["Marigold seeds", "Basil plants", "Nasturtium seeds", "Garlic bulbs"],
        instructions: [
          "Plant marigolds around tomato beds",
          "Interplant basil with tomatoes and peppers",
          "Use nasturtiums as trap crops for aphids",
          "Plant garlic around roses and fruit trees"
        ],
        benefits: [
          "Natural pest deterrent",
          "Attracts beneficial insects",
          "Improves soil health",
          "Provides additional harvest (herbs, flowers)"
        ],
        precautions: [
          "Research plant compatibility",
          "Consider space requirements",
          "Plan for different growing seasons"
        ],
        cost: "medium" as const,
        season: ["Spring", "Summer"]
      },
      {
        name: "Copper Soap Spray",
        disease: "Late Blight, Bacterial Spot, Fire Blight",
        crop: "Tomato, Potato, Apple",
        type: "organic" as const,
        effectiveness: 88,
        duration: "10-14 days",
        difficulty: "medium" as const,
        ingredients: ["Copper sulfate (1 tsp)", "Liquid soap (1 tsp)", "Water (1 liter)"],
        instructions: [
          "Dissolve copper sulfate in small amount of water",
          "Add remaining water and soap",
          "Spray thoroughly on all plant surfaces",
          "Apply before rain events for prevention"
        ],
        benefits: [
          "Highly effective against bacterial diseases",
          "Long-lasting protection",
          "OMRI approved for organic farming",
          "Works in cool, wet conditions"
        ],
        precautions: [
          "Can accumulate in soil over time",
          "May cause phytotoxicity if overused",
          "Wear protective equipment when mixing"
        ],
        cost: "medium" as const,
        season: ["Spring", "Fall"]
      }
    ];

    // Check if treatments already exist
    const existingTreatments = await ctx.db.query("treatments").collect();
    if (existingTreatments.length > 0) {
      return { message: "Treatments already seeded" };
    }

    // Insert treatments
    for (const treatment of treatments) {
      await ctx.db.insert("treatments", treatment);
    }

    return { message: "Treatments seeded successfully", count: treatments.length };
  },
});