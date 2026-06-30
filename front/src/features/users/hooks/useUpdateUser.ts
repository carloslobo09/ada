import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateUser } from "@/features/users/api/usersClient";
import type { UpdateUserInput } from "@/features/users/types";

interface UpdateInput {
  userId: string;
  payload: UpdateUserInput;
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, payload }: UpdateInput) => updateUser(userId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}
