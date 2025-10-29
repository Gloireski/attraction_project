import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  route({
    path: "/",                // root path
    file: "routes/root.tsx",  // root layout component
    loader: async () => null, // optional
    children: [
      index({
        file: "routes/home.tsx", // Home page
        loader: async () => null,
      }),
      route({
        path: "attraction/:id",
        file: "routes/attraction.tsx", // Attraction page
        loader: async () => null,
      }),
    ],
  }),
] satisfies RouteConfig;
