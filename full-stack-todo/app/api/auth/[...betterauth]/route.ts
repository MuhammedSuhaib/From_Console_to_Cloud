import { auth } from "../../../../lib/auth";
export const runtime = "nodejs";

const handler = auth.handler;

export const GET = handler;
export const POST = handler;
export const OPTIONS = handler;
