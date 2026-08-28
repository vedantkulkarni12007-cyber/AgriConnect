import { z } from "zod";
export const lotSchema = z.object({
  crop: z.string().min(2),
  quantity: z.coerce.number().positive(),
  grade: z.enum(["A","B","C"]),
  expected_price: z.coerce.number().positive(),
  location: z.string().min(2),
});
export const offerSchema = z.object({
  quantity: z.coerce.number().positive(),
  price_per_unit: z.coerce.number().positive(),
  message: z.string().optional(),
});
