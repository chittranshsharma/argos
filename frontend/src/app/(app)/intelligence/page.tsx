"use client";

import { useEffect, useState } from "react";
import { getSignalFeed } from "@/lib/api";
import type { Signal } from "@/lib/types";
import SignalFeed from "@/components/SignalFeed";
import { Activity, Filter } from "lucide-react";