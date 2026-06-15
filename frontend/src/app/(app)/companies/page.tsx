"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getCompanies } from "@/lib/api";
import type { Company } from "@/lib/types";
import { useRouter } from "next/navigation";
import { Search, Plus, Activity, ExternalLink, Globe, FileText, RefreshCw } from "lucide-react";