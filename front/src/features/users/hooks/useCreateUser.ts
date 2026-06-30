import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createUser } from "@/features/users/api/usersClient";

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}
