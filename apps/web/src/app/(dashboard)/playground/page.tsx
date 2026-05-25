import type { Metadata } from "next";
import { PlaygroundClient } from "./PlaygroundClient";

export const metadata: Metadata = { title: "Playground" };

export default function PlaygroundPage() {
  return <PlaygroundClient />;
}
