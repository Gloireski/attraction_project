import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  route({
    path: "/",                // root
    file: "routes/root.tsx",
    loader: async () => null, // root loader required
    children: [
      index({
        file: "routes/home.tsx",
        loader: async () => null, // optional, React Query handles data
      }),
      route({
        path: "attraction/:id",
        file: "routes/attraction.tsx",
        loader: async () => null,
      }),
    ],
  }),
] satisfies RouteConfig;
