import { useQuery } from "@tanstack/react-query";
import { listUsers } from "@/features/users/api/usersClient";

export function useListUsers() {
  return useQuery({ queryKey: ["users"], queryFn: listUsers });
}
