"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { addCompany } from "@/lib/api";
import { ArrowLeft, Loader2, Search, Target } from "lucide-react";
import Link from "next/link";