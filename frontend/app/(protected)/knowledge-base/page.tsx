"use client";

import { useEffect, useState } from "react";

import DepartmentCard from "@/components/knowledge/department-card";

import DocumentTable from "@/components/knowledge/document-table";

import UploadDocumentDialog from "@/components/knowledge/upload-document-dialog";

import { getDepartments } from "@/services/department-service";

import { getDocuments } from "@/services/document-service";

import { Department } from "@/types/department";

import { Document } from "@/types/document";

import { useAuth } from "@/contexts/AuthContext";

import LoadingState from "@/components/common/loading-state";
import ErrorCard from "@/components/common/error-card";
import EmptyState from "@/components/common/empty-state";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function KnowledgeBasePage() {
  const [departments, setDepartments] =
    useState<Department[]>([]);

  const [documents, setDocuments] =
    useState<Document[]>([]);

  const [selectedDepartment, setSelectedDepartment] =
    useState("all");

  const { user } = useAuth();

  const isAdmin =
    user?.role === "admin";

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  const filteredDocuments =
    selectedDepartment === "all"
      ? documents
      : documents.filter(
        (doc) =>
          doc.department_id ===
          selectedDepartment
      );

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      if (!isAdmin) {
        return;
      }
      const [
        departmentData,
        documentData,
      ] = await Promise.all([
        getDepartments(),
        getDocuments(),
      ]);

      setDepartments(
        departmentData
      );

      setDocuments(
        documentData
      );
    } catch (error) {
      setError(
        "Unable to load the knowledge base."
      );
    }
    finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  if (!isAdmin) {
    return (
      <div className="space-y-4">

        <h1 className="text-3xl font-bold">
          Knowledge Base
        </h1>

        <div className="rounded-lg border p-6 text-muted-foreground">
          Only administrators can manage the knowledge base.
        </div>

      </div>
    );
  }

  if (loading) {
    return (
      <LoadingState
        title="Loading Knowledge Base"
        description="Fetching departments and documents..."
      />
    );
  }

  if (error) {
    return (
      <ErrorCard
        message={error}
        onRetry={loadData}
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Knowledge Base
          </h1>

          <p className="text-muted-foreground">
            Manage documents and
            departments
          </p>
        </div>

        {isAdmin && (
          <UploadDocumentDialog
            departments={departments}
            onUploaded={loadData}
          />
        )}
      </div>

      <section>
        <h2 className="text-xl font-semibold mb-4">
          Departments
        </h2>

        {departments.length === 0 ? (
          <EmptyState
            title="No departments available"
            description="Create a department before uploading documents."
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {departments.map((dept) => (
              <DepartmentCard
                key={dept.id}
                name={dept.display_name}
                count={dept.document_count}
              />
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="flex justify-between mb-4">
          <h2 className="text-xl font-semibold">
            Documents
          </h2>

          <Select
            value={selectedDepartment}
            onValueChange={
              setSelectedDepartment
            }
          >
            <SelectTrigger className="w-64">
              <SelectValue
                placeholder="Filter Department"
              />
            </SelectTrigger>

            <SelectContent>
              <SelectItem value="all">
                All Departments
              </SelectItem>

              {departments.map((dept) => (
                <SelectItem
                  key={dept.id}
                  value={dept.id}
                >
                  {dept.display_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {filteredDocuments.length === 0 ? (
          <EmptyState
            title="No documents uploaded yet"
            description="Upload your first document to begin building the knowledge base."
          />
        ) : (
          <DocumentTable
            documents={filteredDocuments}
          />
        )}
      </section>
    </div>
  );
}